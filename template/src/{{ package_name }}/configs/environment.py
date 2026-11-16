import os
import re
from typing import Any

_ENV_VAR_PATTERN = re.compile(r"\$\{([^}:]+)(?::-([^}]*))?\}")


def detect_environment() -> str:
    """Determine the active application environment."""
    configured_environment = os.getenv("APP_ENV")

    if configured_environment:
        return configured_environment.strip().lower()

    if os.getenv("K_SERVICE"):
        return "prod"

    return "dev"


def resolve_env_placeholders(value: Any) -> Any:
    """Recursively resolve environment placeholders in configuration values."""
    if isinstance(value, dict):
        return {key: resolve_env_placeholders(item) for key, item in value.items()}

    if isinstance(value, list):
        return [resolve_env_placeholders(item) for item in value]

    if not isinstance(value, str):
        return value

    def replace_placeholder(match: re.Match[str]) -> str:
        variable_name = match.group(1)
        default = match.group(2)
        environment_value = os.getenv(variable_name)

        if environment_value is not None:
            return environment_value

        if default is not None:
            return default

        return match.group(0)

    return _ENV_VAR_PATTERN.sub(replace_placeholder, value)


def override_gcs_bucket_paths(
    config: dict[str, Any],
) -> dict[str, Any]:
    """Replace GCS bucket names in configured paths at runtime."""
    configured_bucket = os.getenv("GCS_BUCKET_NAME")

    if not configured_bucket:
        return config

    bucket_name = configured_bucket.removeprefix("gs://").strip("/")

    if not bucket_name:
        return config

    paths = config.get("paths")

    if not isinstance(paths, dict):
        return config

    new_base_path = f"gs://{bucket_name}"

    for key, path in paths.items():
        if not isinstance(path, str) or not path.startswith("gs://"):
            continue

        path_without_scheme = path.removeprefix("gs://")
        path_parts = path_without_scheme.split("/", maxsplit=1)

        if len(path_parts) == 2:
            paths[key] = f"{new_base_path}/{path_parts[1]}"
        else:
            paths[key] = new_base_path

    return config


def override_cloud_storage_paths(
    config: dict[str, Any],
) -> dict[str, Any]:
    """Apply the selected cloud provider to configured storage paths."""
    provider = os.getenv("CLOUD_PROVIDER", "gcp").strip().lower()

    if provider == "local":
        return config

    if provider == "gcp":
        return override_gcs_bucket_paths(config)

    if provider != "aws":
        raise ValueError("CLOUD_PROVIDER must be one of: local, gcp, aws.")

    configured_bucket = os.getenv("S3_BUCKET_NAME", "").strip()
    bucket_name = configured_bucket.removeprefix("s3://").strip("/")

    if (
        not bucket_name
        or "/" in bucket_name
        or any(character.isspace() for character in bucket_name)
    ):
        raise ValueError("S3_BUCKET_NAME must contain a bucket name without a path.")

    paths = config.get("paths")

    if not isinstance(paths, dict):
        return config

    aws_suffixes = {
        "data_root": "data",
        "raw": "data/raw",
        "interim": "data/interim",
        "processed": "data/processed",
        "artifacts": "artifacts",
        "models": "models",
    }

    for key, path in paths.items():
        if not isinstance(path, str):
            continue

        if path.startswith(("gs://", "s3://")):
            _, _, bucket_and_path = path.partition("://")
            _, separator, suffix = bucket_and_path.partition("/")
            paths[key] = f"s3://{bucket_name}/{suffix}" if separator else f"s3://{bucket_name}"
        elif key in aws_suffixes:
            paths[key] = f"s3://{bucket_name}/{aws_suffixes[key]}"

    return config


def inject_runtime_env(config: dict[str, Any]) -> None:
    """Expose selected configuration values to downstream libraries."""
    services = config.get("services", {})

    if isinstance(services, dict):
        prefect_api_url = services.get("prefect_api_url")

        if prefect_api_url:
            os.environ.setdefault(
                "PREFECT_API_URL",
                str(prefect_api_url),
            )

    tracking = config.get("tracking", {})
    mlflow_tracking_uri = None

    if isinstance(tracking, dict):
        mlflow_tracking_uri = tracking.get("mlflow_tracking_uri")

    if not mlflow_tracking_uri:
        mlflow_tracking_uri = config.get("mlflow_tracking_uri")

    if mlflow_tracking_uri:
        os.environ.setdefault(
            "MLFLOW_TRACKING_URI",
            str(mlflow_tracking_uri),
        )
