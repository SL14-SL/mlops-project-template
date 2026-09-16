from collections.abc import Mapping
from dataclasses import dataclass

from prefect import flow

from ..pipeline.runner import (
    TrackedPipelineResult,
)
from ..pipeline.service import TrainingPipeline
from ..tracking.lifecycle import (
    CandidateLifecycleResult,
    finalize_configured_model_candidate,
)
from ..tracking.mlflow import (
    log_evaluation_result,
    log_training_result,
    start_training_run,
)
from .prefect_adapter import (
    run_prefect_training_pipeline,
)


@dataclass(frozen=True)
class PrefectTrainingLifecycleResult:
    """Complete result of training and model finalization."""

    pipeline: TrackedPipelineResult
    candidate: CandidateLifecycleResult


@flow(
    name="training-model-lifecycle",
    validate_parameters=False,
    persist_result=False,
)
def run_prefect_model_lifecycle(
    *,
    pipeline: TrainingPipeline,
    pipeline_run_id: str | None = None,
    mlflow_run_name: str | None = None,
    mlflow_tags: Mapping[str, str] | None = None,
    artifact_path: str = "model",
) -> PrefectTrainingLifecycleResult:
    """Run training, MLflow logging and model finalization."""

    with start_training_run(
        pipeline.config,
        run_name=mlflow_run_name,
        tags=mlflow_tags,
    ) as mlflow_run_id:
        tracked_result = (
            run_prefect_training_pipeline(
                pipeline=pipeline,
                run_id=(
                    pipeline_run_id
                    or mlflow_run_id
                ),
            )
        )

        pipeline_result = (
            tracked_result.pipeline
        )

        log_training_result(
            pipeline_result.training
        )
        log_evaluation_result(
            pipeline_result.evaluation
        )

    candidate_result = (
        finalize_configured_model_candidate(
            training_result=(
                pipeline_result.training
            ),
            evaluation_result=(
                pipeline_result.evaluation
            ),
            config=pipeline.config,
            artifact_path=artifact_path,
        )
    )

    return PrefectTrainingLifecycleResult(
        pipeline=tracked_result,
        candidate=candidate_result,
    )