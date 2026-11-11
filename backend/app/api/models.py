from __future__ import annotations

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException

from app.api.deps import current_principal, get_registry
from app.core.registry import Registry

router = APIRouter(tags=["models"], dependencies=[Depends(current_principal)])


@router.get("/models")
def model_card(reg: Annotated[Registry, Depends(get_registry)]) -> Any:
    """Trả nguyên văn `model_card.json` (danh sách model); không thêm, không sửa số liệu."""
    if reg.model_card is None:
        raise HTTPException(
            status_code=503, detail="Chưa có models/model_card.json (model đang huấn luyện)"
        )
    return reg.model_card
