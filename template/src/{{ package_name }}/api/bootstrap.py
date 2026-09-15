from typing import Any

from fastapi import FastAPI

from ..configs.loader import load_config
from ..inference.model_manager import ModelManager
from ..inference.serving import load_active_bundle
from .app import create_app


def build_model_manager(
    config: dict[str, Any],
) -> ModelManager:
    """Build a model manager from application configuration."""

    def bundle_loader():
        return load_active_bundle(config)

    return ModelManager(bundle_loader)


def build_application(
    *,
    config: dict[str, Any] | None = None,
    load_model_on_startup: bool = True,
) -> FastAPI:
    """Build the configured FastAPI application."""
    application_config = (
        config
        if config is not None
        else load_config()
    )
    model_manager = build_model_manager(
        application_config
    )

    project = application_config.get("project", {})
    project_name = (
        project.get("name")
        if isinstance(project, dict)
        else None
    )
    application_title = (
        f"{project_name} API"
        if isinstance(project_name, str)
        and project_name.strip()
        else "MLOps Model API"
    )

    return create_app(
        model_manager=model_manager,
        load_model_on_startup=load_model_on_startup,
        title=application_title,
    )