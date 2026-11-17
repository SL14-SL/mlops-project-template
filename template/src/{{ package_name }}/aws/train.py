"""Train and export one candidate without registry promotion."""

import argparse
import json
import os
import shutil

from collections.abc import Callable
from copy import deepcopy
from pathlib import Path
from typing import Any

import mlflow
import yaml
from mlflow import MlflowClient
from mlflow.tracking._model_registry import utils as registry_utils
from mlflow.tracking._tracking_service import utils as tracking_utils

from ..configs.environment import resolve_env_placeholders
from ..inference.releases.input_provider import build_serving_release_input
from ..pipeline.project_factory import build_project_training_pipeline
from ..pipeline.runner import run_training_pipeline
from ..pipeline.service import TrainingPipeline
from ..tracking.mlflow import log_evaluation_result, log_training_result
from ..tracking.model_artifact import log_model_artifact
from .candidate import export_candidate_serving_input
from .training_config import TrainingJobPaths, prepare_training_job_paths

PipelineFactory = Callable[[dict[str, Any]], TrainingPipeline]


def build_job_config(
    config_path: Path,
    paths: TrainingJobPaths,
) -> dict[str, Any]:
    """Load YAML directly and replace project paths with isolated paths."""
    with config_path.open("r", encoding="utf-8") as file:
        payload = yaml.safe_load(file)

    if not isinstance(payload, dict):
        raise ValueError("Training configuration must contain a YAML mapping.")

    config = deepcopy(resolve_env_placeholders(payload))
    configured_paths = config.get("paths", {})

    if not isinstance(configured_paths, dict):
        raise ValueError("Training configuration paths must be a mapping.")

    local_paths = {
        "data_root": paths.work_directory / "data",
        "raw": paths.input_directory,
        "interim": paths.work_directory / "data/interim",
        "processed": paths.work_directory / "data/processed",
        "artifacts": paths.work_directory / "artifacts",
        "models": paths.work_directory / "models",
    }

    unknown_paths = configured_paths.keys() - local_paths.keys()

    if unknown_paths:
        raise ValueError(
            "Define isolated mappings before using additional training paths: "
            f"{sorted(unknown_paths)}"
        )

    config["paths"] = {name: str(directory) for name, directory in local_paths.items()}
    config["environment"] = "isolated-training"

    tracking = config.setdefault("tracking", {})

    if not isinstance(tracking, dict):
        raise ValueError("Training configuration tracking must be a mapping.")

    tracking["mlflow_tracking_uri"] = f"sqlite:///{paths.work_directory / 'mlflow.db'}"
    tracking["experiment_name"] = "isolated-training-job"

    return config


def run_training_job(
    *,
    config_path: Path,
    paths: TrainingJobPaths,
    pipeline_factory: PipelineFactory = build_project_training_pipeline,
) -> dict[str, Any]:
    """Execute the training adapters and export a model candidate."""
    if mlflow.active_run() is not None:
        raise RuntimeError("An isolated job requires no active MLflow run.")

    config = build_job_config(config_path, paths)
    tracking_uri = config["tracking"]["mlflow_tracking_uri"]
    # Preserve explicit configuration, including an unset registry that
    # should continue following the tracking URI after this job.
    previous_tracking_uri = tracking_utils._tracking_uri
    previous_registry_uri = registry_utils._registry_uri
    previous_environment = {
        name: os.environ.get(name) for name in ("MLFLOW_TRACKING_URI", "MLFLOW_REGISTRY_URI")
    }

    try:
        mlflow.set_tracking_uri(tracking_uri)
        mlflow.set_registry_uri(tracking_uri)

        client = MlflowClient(tracking_uri=tracking_uri)
        experiment_id = client.create_experiment(
            config["tracking"]["experiment_name"],
            artifact_location=(paths.work_directory / "mlruns").as_uri(),
        )
        pipeline = pipeline_factory(config)

        if not isinstance(pipeline, TrainingPipeline):
            raise TypeError("Pipeline factory must return TrainingPipeline.")

        with mlflow.start_run(experiment_id=experiment_id) as active_run:
            result = run_training_pipeline(
                ingestor=pipeline.ingestor,
                feature_builder=pipeline.feature_builder,
                splitter=pipeline.splitter,
                trainer=pipeline.trainer,
                evaluator=pipeline.evaluator,
                config=config,
            )
            log_training_result(result.training)
            log_evaluation_result(result.evaluation)

            logged_model = log_model_artifact(
                logger=pipeline.model_logger,
                training_result=result.training,
                config=config,
            )

            download_directory = paths.work_directory / "download"
            download_directory.mkdir()
            downloaded = Path(
                mlflow.artifacts.download_artifacts(
                    artifact_uri=logged_model.model_uri,
                    dst_path=str(download_directory),
                )
            ).resolve()

            if (
                not downloaded.is_dir()
                or paths.work_directory.resolve() not in downloaded.parents
                or not (downloaded / "MLmodel").is_file()
            ):
                raise ValueError(
                    "Export requires an MLflow model inside the isolated "
                    f"job work directory; received: {downloaded}"
                )

            shutil.copytree(
                downloaded,
                paths.model_directory / "model",
            )

            release_input = build_serving_release_input(
                provider=pipeline.release_input_provider,
                training_result=result.training,
                evaluation_result=result.evaluation,
                config=config,
            )
            export_candidate_serving_input(
                release_input=release_input,
                paths=paths,
                run_id=result.training.run_id,
            )

            report = {
                "schema_version": 1,
                "run_id": active_run.info.run_id,
                "training_rows": len(result.splits.train),
                "validation_rows": len(result.splits.validation),
                "training_metrics": {
                    name: float(value) for name, value in result.training.metrics.items()
                },
                "evaluation_metrics": {
                    name: float(value) for name, value in result.evaluation.metrics.items()
                },
                "evaluation_approved": result.evaluation.approved,
                "evaluation_reasons": list(result.evaluation.reasons),
                "promoted": False,
            }
            serialized = (
                json.dumps(
                    report,
                    indent=2,
                    sort_keys=True,
                    allow_nan=False,
                )
                + "\n"
            )
            (paths.output_directory / "evaluation.json").write_text(
                serialized,
                encoding="utf-8",
            )

        return report
    finally:
        mlflow.set_tracking_uri(previous_tracking_uri)
        mlflow.set_registry_uri(previous_registry_uri)

        for name, value in previous_environment.items():
            if value is None:
                os.environ.pop(name, None)
            else:
                os.environ[name] = value


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=["train"], default="train")
    parser.add_argument("--config", type=Path, default=Path("configs/dev.yaml"))
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--model-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()

    paths = prepare_training_job_paths(
        input_directory=args.input_dir,
        work_directory=args.work_dir,
        model_directory=args.model_dir,
        output_directory=args.output_dir,
    )
    report = run_training_job(
        config_path=args.config.resolve(),
        paths=paths,
    )
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
