"""Add project-owned adapters and tests to a generated update-test project."""

import argparse
from pathlib import Path

ADAPTER_SOURCE = """\
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

import pandas as pd

from __PACKAGE__.data.contracts import DatasetSplits
from __PACKAGE__.training.contracts import EvaluationResult, TrainingResult


@dataclass(frozen=True)
class ConstantModel:
    value: float

    def predict(self, inputs: pd.DataFrame) -> list[float]:
        return [self.value] * len(inputs)


class ProjectTrainer:
    def train(
        self,
        datasets: DatasetSplits,
        config: Mapping[str, Any],
    ) -> TrainingResult:
        value = float(datasets.train["target"].mean())

        return TrainingResult(
            model=ConstantModel(value),
            run_id=str(config["run_id"]),
            metrics={"training_mean": value},
            parameters={"strategy": "constant-mean"},
        )


class ProjectEvaluator:
    def evaluate(
        self,
        training_result: TrainingResult,
        datasets: DatasetSplits,
        config: Mapping[str, Any],
    ) -> EvaluationResult:
        predictions = training_result.model.predict(datasets.validation)
        targets = datasets.validation["target"].tolist()
        mae = sum(
            abs(prediction - target)
            for prediction, target in zip(predictions, targets, strict=True)
        ) / len(targets)
        approved = mae <= float(config["maximum_mae"])

        return EvaluationResult(
            metrics={"mae": mae},
            approved=approved,
            reasons=() if approved else ("MAE exceeds project limit.",),
        )
"""

TEST_SOURCE = """\
import pandas as pd
import pytest

from __PACKAGE__.data.contracts import DatasetSplits
from __PACKAGE__.project_extension import ProjectEvaluator, ProjectTrainer
from __PACKAGE__.training.contracts import ModelEvaluator, ModelTrainer


def test_project_adapters_implement_training_contracts() -> None:
    trainer = ProjectTrainer()
    evaluator = ProjectEvaluator()

    assert isinstance(trainer, ModelTrainer)
    assert isinstance(evaluator, ModelEvaluator)

    datasets = DatasetSplits(
        train=pd.DataFrame({"target": [2.0, 4.0]}),
        validation=pd.DataFrame({"target": [3.0, 5.0]}),
    )
    config = {
        "run_id": "compatibility-fixture-run",
        "maximum_mae": 1.0,
    }

    trained = trainer.train(datasets, config)
    evaluated = evaluator.evaluate(trained, datasets, config)

    assert trained.run_id == "compatibility-fixture-run"
    assert trained.parameters == {"strategy": "constant-mean"}
    assert trained.model.predict(datasets.validation) == [3.0, 3.0]
    assert evaluated.metrics["mae"] == pytest.approx(1.0)
    assert evaluated.approved is True
    assert evaluated.reasons == ()


def test_project_evaluation_can_reject_candidate() -> None:
    datasets = DatasetSplits(
        train=pd.DataFrame({"target": [2.0, 4.0]}),
        validation=pd.DataFrame({"target": [3.0, 5.0]}),
    )
    config = {
        "run_id": "compatibility-fixture-run",
        "maximum_mae": 0.5,
    }

    trained = ProjectTrainer().train(datasets, config)
    evaluated = ProjectEvaluator().evaluate(trained, datasets, config)

    assert evaluated.approved is False
    assert evaluated.reasons == ("MAE exceeds project limit.",)
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("project_root", type=Path)
    parser.add_argument("package_name")
    args = parser.parse_args()

    package_directory = args.project_root / "src" / args.package_name

    if not package_directory.is_dir():
        raise FileNotFoundError(package_directory)

    files = {
        package_directory / "project_extension.py": ADAPTER_SOURCE,
        args.project_root / "tests/unit/test_project_extension.py": TEST_SOURCE,
    }

    for destination in files:
        if destination.exists():
            raise FileExistsError(destination)

    for destination, source in files.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(
            source.replace("__PACKAGE__", args.package_name),
            encoding="utf-8",
        )


if __name__ == "__main__":
    main()
