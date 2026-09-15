from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from ...inference.model_manager import (
    ModelManager,
    ModelNotReadyError,
)
from ...inference.prediction_service import PredictionService
from ..dependencies import (
    get_model_manager,
    require_api_key,
)
from ..schema import (
    PredictionRequest,
    PredictionResponse,
)

router = APIRouter(tags=["prediction"])


@router.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(
    request: PredictionRequest,
    _: Annotated[
        None,
        Depends(require_api_key),
    ],
    model_manager: Annotated[
        ModelManager | None,
        Depends(get_model_manager),
    ],
) -> PredictionResponse:
    """Run a prediction using the active serving bundle."""
    if model_manager is None or not model_manager.ready:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction service is not ready.",
        )

    service = PredictionService(model_manager)

    try:
        return service.predict(request)
    except ModelNotReadyError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Prediction service is not ready.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(exc),
        ) from exc