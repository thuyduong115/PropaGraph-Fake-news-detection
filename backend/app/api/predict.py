from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import current_principal, get_registry
from app.core.registry import Registry
from app.schemas.graphs import PredictRequest, PredictResponse
from app.services import inference

router = APIRouter(tags=["predict"], dependencies=[Depends(current_principal)])


@router.post("/predict", response_model=PredictResponse)
def predict(
    body: PredictRequest, reg: Annotated[Registry, Depends(get_registry)]
) -> PredictResponse:
    """Chỉ nhận `gid` có sẵn trong tập demo (DATA_BOUNDARY.md mục 4)."""
    if body.gid not in reg.graphs.get(body.dataset, {}):
        raise HTTPException(status_code=404, detail=f"Không có đồ thị {body.gid}")
    try:
        result = inference.predict(reg, body.dataset, body.gid, body.feature, body.cutoff_h)
    except inference.ModelUnavailable as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    return PredictResponse(**result)
