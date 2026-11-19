"""AWS entry point for the same lifecycle used by local and GCP projects."""

import argparse
import json
import os
from typing import Any
from urllib.parse import urlsplit

from ..configs.loader import load_config
from ..orchestration.lifecycle_adapter import run_prefect_model_lifecycle
from ..orchestration.retraining_service import run_auto_retraining
from ..pipeline.project_factory import build_project_training_pipeline


def load_aws_lifecycle_config() -> dict[str, Any]:
    """Resolve S3 paths and require a shared, reachable tracking service."""
    if os.environ.get("CLOUD_PROVIDER") != "aws":
        raise ValueError("Set CLOUD_PROVIDER=aws for the AWS lifecycle.")
    config = load_config()
    if not all(
        isinstance(value, str) and value.startswith("s3://") for value in config["paths"].values()
    ):
        raise ValueError("AWS lifecycle requires resolved S3 project paths.")
    tracking_uri = config["tracking"]["mlflow_tracking_uri"]
    parsed = urlsplit(tracking_uri)
    if (
        parsed.scheme not in {"http", "https"}
        or not parsed.hostname
        or parsed.hostname
        in {
            "localhost",
            "127.0.0.1",
            "::1",
        }
    ):
        raise ValueError("AWS lifecycle requires a shared HTTP(S) MLFLOW_TRACKING_URI.")
    return config


def run_aws_lifecycle(*, mode: str = "train", evaluated_at: str | None = None) -> dict[str, Any]:
    """Train or evaluate retraining signals using the shared lifecycle services."""
    if mode not in {"train", "auto-retrain"}:
        raise ValueError("mode must be train or auto-retrain.")
    config = load_aws_lifecycle_config()
    if mode == "auto-retrain":

        def after_lifecycle(result):
            if result.serving_release is not None:
                _refresh_promoted_release(config)

        return run_auto_retraining(
            config=config, evaluated_at=evaluated_at, after_lifecycle=after_lifecycle
        )
    result = run_prefect_model_lifecycle(
        pipeline=build_project_training_pipeline(config),
        mlflow_tags={"cloud.provider": "aws"},
    )
    if result.serving_release is not None:
        _refresh_promoted_release(config)
    from ..orchestration.retraining_service import record_training_completion

    record_training_completion(config=config, evaluated_at=evaluated_at)
    candidate = result.candidate
    return {
        "run_id": result.pipeline.pipeline.training.run_id,
        "registered": candidate.registration.registered,
        "model_version": candidate.registration.model_version,
        "promoted": result.serving_release is not None,
        "release_id": (
            result.serving_release.manifest.release_id if result.serving_release else None
        ),
        "promotion_reason": candidate.promotion.decision.reason if candidate.promotion else None,
    }


def _refresh_promoted_release(config: dict[str, Any]) -> None:
    """Apply a new S3 pointer to ECS when serving is configured."""
    if not os.environ.get("AWS_API_SERVICE"):
        return  # Bootstrap training can precede the first API deployment.
    from ..inference.releases.pointer import load_active_release_pointer
    from .operations import refresh_service, rollback_model

    pointer = load_active_release_pointer(models_path=config["paths"]["models"])
    try:
        refresh_service(expected_release_id=pointer.release_id)
    except Exception as deployment_error:
        if pointer.previous_release_id is None:
            raise RuntimeError(
                "Initial model was published, but ECS refresh failed; no previous release exists."
            ) from deployment_error
        try:
            rollback_model(config=config)
        except Exception as rollback_error:
            raise ExceptionGroup(
                "ECS refresh and model rollback failed.", [deployment_error, rollback_error]
            ) from None
        raise


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mode",
        choices=["train", "auto-retrain", "rollback-model", "refresh"],
        nargs="?",
        default="train",
    )
    parser.add_argument(
        "--evaluated-at", help="Optional explicit logical evaluation time in ISO 8601 format"
    )
    args = parser.parse_args()
    if args.mode in {"rollback-model", "refresh"}:
        from ..inference.releases.pointer import load_active_release_pointer
        from .operations import refresh_service, rollback_model

        config = load_aws_lifecycle_config()
        if args.mode == "rollback-model":
            release_id = rollback_model(config=config)
        else:
            release_id = load_active_release_pointer(
                models_path=config["paths"]["models"]
            ).release_id
            refresh_service(expected_release_id=release_id)
        report = {"release_id": release_id, "operation": args.mode}
    else:
        report = run_aws_lifecycle(mode=args.mode, evaluated_at=args.evaluated_at)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
