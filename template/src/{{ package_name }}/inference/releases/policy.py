from .contracts import (
    ServingReleaseManifest,
    TaskType,
    validate_serving_manifest,
)

_CLASSIFICATION_ARTIFACTS = {
    "feature_schema",
}

_FORECASTING_ARTIFACTS = {
    "store_metadata",
    "store_state",
    "known_calendar",
}


def _require_artifacts(
    manifest: ServingReleaseManifest,
    required_artifacts: set[str],
) -> None:
    """Require task-specific artifacts in a release manifest."""
    missing_artifacts = (
        required_artifacts - manifest.artifacts.keys()
    )

    if missing_artifacts:
        raise ValueError(
            "Serving manifest is missing required artifacts: "
            f"{sorted(missing_artifacts)}."
        )


def validate_classification_manifest(
    manifest: ServingReleaseManifest,
) -> None:
    """Validate classification-specific release requirements."""
    validate_serving_manifest(manifest)

    if manifest.task_type is not TaskType.CLASSIFICATION:
        raise ValueError(
            "Expected a classification serving manifest."
        )

    _require_artifacts(
        manifest,
        _CLASSIFICATION_ARTIFACTS,
    )

    metadata = manifest.metadata or {}
    decision_threshold = metadata.get("decision_threshold")

    if (
        isinstance(decision_threshold, bool)
        or not isinstance(decision_threshold, (int, float))
    ):
        raise ValueError(
            "Classification serving manifest requires a numeric "
            "decision_threshold."
        )

    if not 0.0 <= float(decision_threshold) <= 1.0:
        raise ValueError(
            "Classification decision_threshold must be "
            "between 0 and 1."
        )


def validate_forecasting_manifest(
    manifest: ServingReleaseManifest,
) -> None:
    """Validate forecasting-specific release requirements."""
    validate_serving_manifest(manifest)

    if manifest.task_type is not TaskType.FORECASTING:
        raise ValueError(
            "Expected a forecasting serving manifest."
        )

    _require_artifacts(
        manifest,
        _FORECASTING_ARTIFACTS,
    )

    metadata = manifest.metadata or {}
    target_transformation = metadata.get(
        "target_transformation"
    )

    if (
        not isinstance(target_transformation, str)
        or not target_transformation.strip()
    ):
        raise ValueError(
            "Forecasting serving manifest requires a "
            "target_transformation."
        )


def validate_task_manifest(
    manifest: ServingReleaseManifest,
) -> None:
    """Apply validation for the manifest's machine-learning task."""
    if manifest.task_type is TaskType.CLASSIFICATION:
        validate_classification_manifest(manifest)
        return

    if manifest.task_type is TaskType.FORECASTING:
        validate_forecasting_manifest(manifest)
        return

    raise ValueError(
        f"Unsupported serving task type: {manifest.task_type}."
    )