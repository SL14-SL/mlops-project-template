from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd

from ..data.contracts import (
    DataIngestor,
    DatasetCollection,
    DatasetSplits,
    DatasetSplitter,
    FeatureBuilder,
)
from ..training.contracts import (
    EvaluationResult,
    ModelEvaluator,
    ModelTrainer,
    TrainingResult,
)


@dataclass(frozen=True)
class PipelineResult:
    """Complete result of one training-pipeline execution."""

    datasets: DatasetCollection
    features: pd.DataFrame
    splits: DatasetSplits
    training: TrainingResult
    evaluation: EvaluationResult


def _validate_features(
    features: object,
) -> pd.DataFrame:
    """Validate the result of feature engineering."""
    if not isinstance(features, pd.DataFrame):
        raise TypeError(
            "Feature builder must return a pandas DataFrame."
        )

    if features.empty:
        raise ValueError(
            "Feature builder returned an empty DataFrame."
        )

    return features


def _validate_splits(
    splits: object,
) -> DatasetSplits:
    """Validate the result of dataset splitting."""
    if not isinstance(splits, DatasetSplits):
        raise TypeError(
            "Dataset splitter must return DatasetSplits."
        )

    return splits


def _validate_training_result(
    result: object,
) -> TrainingResult:
    """Validate the result of model training."""
    if not isinstance(result, TrainingResult):
        raise TypeError(
            "Model trainer must return TrainingResult."
        )

    return result


def _validate_evaluation_result(
    result: object,
) -> EvaluationResult:
    """Validate the result of model evaluation."""
    if not isinstance(result, EvaluationResult):
        raise TypeError(
            "Model evaluator must return EvaluationResult."
        )

    return result


def run_training_pipeline(
    *,
    ingestor: DataIngestor,
    feature_builder: FeatureBuilder,
    splitter: DatasetSplitter,
    trainer: ModelTrainer,
    evaluator: ModelEvaluator,
    config: Mapping[str, Any],
) -> PipelineResult:
    """Execute the framework-independent training pipeline."""
    datasets = ingestor.ingest(config)

    if not isinstance(datasets, DatasetCollection):
        raise TypeError(
            "Data ingestor must return DatasetCollection."
        )

    features = _validate_features(
        feature_builder.build_features(
            datasets,
            config,
        )
    )
    splits = _validate_splits(
        splitter.split(
            features,
            config,
        )
    )
    training_result = _validate_training_result(
        trainer.train(
            splits,
            config,
        )
    )
    evaluation_result = _validate_evaluation_result(
        evaluator.evaluate(
            training_result,
            splits,
            config,
        )
    )

    return PipelineResult(
        datasets=datasets,
        features=features,
        splits=splits,
        training=training_result,
        evaluation=evaluation_result,
    )