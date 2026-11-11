from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import get_registry
from app.core.registry import Registry

router = APIRouter(tags=["models"])


@router.get("/models")
def model_card(reg: Annotated[Registry, Depends(get_registry)]) -> dict[str, Any]:
    """Trả nguyên văn `model_card.json`; không thêm, không sửa số liệu."""
    if reg.model_card is None:
        raise HTTPException(status_code=503, detail="Chưa nạp được models/model_card.json")
    return reg.model_card
