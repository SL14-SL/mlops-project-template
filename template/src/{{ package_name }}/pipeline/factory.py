from collections.abc import Mapping
from typing import Any

from .store import PipelineRunStore


def _require_paths(
    config: Mapping[str, Any],
) -> Mapping[str, Any]:
    """Return the validated paths configuration."""
    paths = config.get("paths")

    if not isinstance(paths, Mapping):
        raise ValueError(
            "Config must contain a valid 'paths' section."
        )

    return paths


def _require_path(
    paths: Mapping[str, Any],
    name: str,
) -> str:
    """Return one resolved path configuration value."""
    value = paths.get(name)

    if (
        not isinstance(value, str)
        or not value.strip()
        or value.startswith("${")
    ):
        raise ValueError(
            f"Config path '{name}' must be "
            "a resolved non-empty string."
        )

    return value.rstrip("/")


def build_pipeline_run_store(
    config: Mapping[str, Any],
) -> PipelineRunStore:
    """Build the configured pipeline lifecycle store."""
    paths = _require_paths(config)
    configured_path = paths.get(
        "pipeline_runs"
    )

    if configured_path is not None:
        root_path = _require_path(
            paths,
            "pipeline_runs",
        )
    else:
        artifacts_path = _require_path(
            paths,
            "artifacts",
        )
        root_path = (
            f"{artifacts_path}/pipeline-runs"
        )

    return PipelineRunStore(root_path)