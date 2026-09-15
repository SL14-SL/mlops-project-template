from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from ..inference.model_manager import ModelManager
from ..utils.logger import get_logger
from .routers.health import router as health_router

logger = get_logger(__name__)


def create_app(
    *,
    model_manager: ModelManager | None = None,
    load_model_on_startup: bool = True,
    title: str = "MLOps Model API",
) -> FastAPI:
    """Create and configure the FastAPI application."""

    @asynccontextmanager
    async def lifespan(
        app: FastAPI,
    ) -> AsyncIterator[None]:
        if (
            model_manager is not None
            and load_model_on_startup
        ):
            try:
                model_manager.load_initial()
            except Exception as exc:
                logger.error(
                    "Initial serving bundle load failed: %s",
                    exc,
                )

        yield

    app = FastAPI(
        title=title,
        version="0.1.0",
        lifespan=lifespan,
    )
    app.state.model_manager = model_manager
    app.include_router(health_router)

    return app