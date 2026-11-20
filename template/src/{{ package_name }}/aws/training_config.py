from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TrainingJobPaths:
    """Local directories belonging to one isolated training job."""

    input_directory: Path
    work_directory: Path
    model_directory: Path
    output_directory: Path


def _resolve_local_directory(value: str | Path) -> Path:
    """Resolve a local directory without accepting remote URIs."""
    if "://" in str(value):
        raise ValueError("Training job directories must be local paths.")

    return Path(value).expanduser().resolve()


def prepare_training_job_paths(
    *,
    input_directory: str | Path,
    work_directory: str | Path,
    model_directory: str | Path,
    output_directory: str | Path,
) -> TrainingJobPaths:
    """Validate isolation before creating empty job directories."""
    paths = TrainingJobPaths(
        input_directory=_resolve_local_directory(input_directory),
        work_directory=_resolve_local_directory(work_directory),
        model_directory=_resolve_local_directory(model_directory),
        output_directory=_resolve_local_directory(output_directory),
    )
    directories = (
        paths.input_directory,
        paths.work_directory,
        paths.model_directory,
        paths.output_directory,
    )

    for index, directory in enumerate(directories):
        for other in directories[index + 1 :]:
            if directory == other or directory in other.parents or other in directory.parents:
                raise ValueError(
                    f"Training job directories must not overlap: {directory} and {other}"
                )

    if not paths.input_directory.is_dir():
        raise FileNotFoundError(f"Training input directory not found: {paths.input_directory}")

    destinations = (
        paths.work_directory,
        paths.model_directory,
        paths.output_directory,
    )

    for directory in destinations:
        if directory.exists():
            if not directory.is_dir():
                raise ValueError(f"Training destination is not a directory: {directory}")

            if any(directory.iterdir()):
                raise ValueError(f"Training destination must be empty: {directory}")

    for directory in destinations:
        directory.mkdir(parents=True, exist_ok=True)

    return paths
