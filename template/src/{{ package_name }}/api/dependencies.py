from fastapi import Request

from ..inference.model_manager import ModelManager


def get_model_manager(
    request: Request,
) -> ModelManager | None:
    """Return the application's model manager."""
    return getattr(
        request.app.state,
        "model_manager",
        None,
    )