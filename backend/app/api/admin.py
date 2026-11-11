from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.api.deps import get_registry, require_admin
from app.core.registry import Registry
from app.schemas.auth import AdminStatus

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin)])


def _status(reg: Registry) -> AdminStatus:
    return AdminStatus(
        artifacts_dir=str(reg.artifacts_dir),
        loaded_at=reg.loaded_at,
        synthetic=reg.synthetic,
        datasets={ds: len(g) for ds, g in reg.graphs.items()},
        tables=sorted(reg.tables),
        figures=len(reg.figures),
        model_card=reg.model_card is not None,
        models_loaded=sorted(reg.models),
        problems=reg.problems,
        notes=reg.notes,
    )


@router.get("/status", response_model=AdminStatus)
def status(reg: Annotated[Registry, Depends(get_registry)]) -> AdminStatus:
    return _status(reg)


@router.post("/reload", response_model=AdminStatus)
def reload(request: Request) -> AdminStatus:
    """Nạp lại artifacts sau khi copy bản export mới, không cần khởi động lại backend.
    Chỉ đọc `artifacts/`, không ghi."""
    reg = Registry.load(request.app.state.settings.artifacts_path)
    request.app.state.registry = reg
    return _status(reg)
