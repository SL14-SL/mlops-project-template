import re
import time
from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response
from fastapi.responses import JSONResponse

from ..utils.logger import get_logger

logger = get_logger(__name__)

_REQUEST_ID_PATTERN = re.compile(
    r"^[A-Za-z0-9._-]{1,128}$"
)


def _request_id_from_request(
    request: Request,
) -> str:
    """Return a safe request ID or generate a new one."""
    provided_request_id = request.headers.get(
        "X-Request-ID"
    )

    if (
        provided_request_id
        and _REQUEST_ID_PATTERN.fullmatch(
            provided_request_id
        )
    ):
        return provided_request_id

    return str(uuid4())


def _duration_ms(started_at: float) -> str:
    """Return elapsed milliseconds formatted for a response header."""
    elapsed_seconds = time.perf_counter() - started_at
    return f"{elapsed_seconds * 1000:.2f}"


async def request_context_middleware(
    request: Request,
    call_next: Callable[
        [Request],
        Awaitable[Response],
    ],
) -> Response:
    """Add request context, timing and safe error handling."""
    request_id = _request_id_from_request(request)
    request.state.request_id = request_id
    started_at = time.perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception(
            "Unhandled API error | request_id=%s | method=%s | path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        response = JSONResponse(
            status_code=500,
            content={
                "status": "error",
                "error": "internal_server_error",
                "request_id": request_id,
            },
        )

    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = (
        _duration_ms(started_at)
    )
    return response