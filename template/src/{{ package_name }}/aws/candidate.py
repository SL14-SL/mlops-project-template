"""Export portable serving inputs without activating a release."""

import json
import shutil
from pathlib import Path, PurePosixPath
from typing import Any

from ..inference.releases.input_provider import ServingReleaseInput
from ..inference.releases.storage import sha256_uri
from .training_config import TrainingJobPaths


def _relative_artifact_path(value: str) -> str:
    """Require an unambiguous release-relative POSIX file path."""
    path = PurePosixPath(value)

    if (
        not value
        or path.is_absolute()
        or "\\" in value
        or ":" in value
        or ".." in path.parts
        or value != path.as_posix()
        or value == "."
    ):
        raise ValueError(f"Candidate artifact path must be relative: {value!r}")

    return value


def export_candidate_serving_input(
    *,
    release_input: ServingReleaseInput,
    paths: TrainingJobPaths,
    run_id: str,
) -> dict[str, Any]:
    """Export local serving artifacts and checksums for one candidate."""
    model_root = paths.model_directory / "model"

    if not (model_root / "MLmodel").is_file():
        raise FileNotFoundError("Candidate export requires an MLflow model.")

    destination = paths.model_directory / "candidate.json"
    artifact_root = paths.model_directory / "serving_artifacts"

    if destination.exists() or artifact_root.exists():
        raise FileExistsError("Candidate serving export already exists.")

    sources: list[tuple[str, Path, str]] = []
    destinations: set[str] = set()

    for name, source in release_input.sources.items():
        relative_path = _relative_artifact_path(source.relative_path)

        if relative_path in destinations:
            raise ValueError("Candidate artifact destinations must be unique.")

        destinations.add(relative_path)

        if "://" in source.source_uri:
            raise ValueError("Candidate artifact sources must be local files.")

        source_path = Path(source.source_uri).resolve()

        if not any(
            root.resolve() in source_path.parents
            for root in (paths.input_directory, paths.work_directory)
        ):
            raise ValueError("Candidate sources must be inside the job input or work directory.")

        if not source_path.is_file():
            raise FileNotFoundError(source_path)

        sources.append((name, source_path, relative_path))

    model_files = {}

    for model_file in sorted(model_root.rglob("*")):
        if model_file.is_symlink():
            raise ValueError("Candidate model files must not be symlinks.")

        if model_file.is_file():
            relative_path = model_file.relative_to(paths.model_directory).as_posix()
            model_files[relative_path] = sha256_uri(str(model_file))

    payload = {
        "schema_version": 1,
        "run_id": run_id,
        "task_type": release_input.task_type.value,
        "model_type": release_input.model_type,
        "model_path": "model",
        "model_files": model_files,
        "metadata": dict(release_input.metadata),
        "dataset_version": release_input.dataset_version,
        "config_hash": release_input.config_hash,
        "git_commit": release_input.git_commit,
        "artifacts": {},
        "promoted": False,
    }

    # Reject non-JSON metadata before copying serving artifacts.
    json.dumps(payload, allow_nan=False)

    artifact_root.mkdir()

    for name, source_path, relative_path in sources:
        target = artifact_root / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source_path, target)
        payload["artifacts"][name] = {
            "path": target.relative_to(paths.model_directory).as_posix(),
            "sha256": sha256_uri(str(target)),
        }

    destination.write_text(
        json.dumps(
            payload,
            indent=2,
            sort_keys=True,
            allow_nan=False,
        )
        + "\n",
        encoding="utf-8",
    )
    return payload
