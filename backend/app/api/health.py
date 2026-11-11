from __future__ import annotations

import importlib.metadata
from typing import Annotated

from fastapi import APIRouter, Depends

from app import __version__
from app.api.deps import get_auth, get_registry
from app.core.auth import Authenticator
from app.core.registry import Registry
from app.schemas.health import Health

router = APIRouter(tags=["health"])


def _version(dist: str) -> str | None:
    try:
        return importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError:
        return None


@router.get("/health", response_model=Health)
def health(
    reg: Annotated[Registry, Depends(get_registry)],
    auth: Annotated[Authenticator, Depends(get_auth)],
) -> Health:
    """Công khai. Báo đúng tình trạng: thiếu dữ liệu thì `degraded` kèm danh sách vấn đề.
    Không lộ đường dẫn trên máy chủ (xem `/api/admin/status`)."""
    return Health(
        status="ok" if reg.ready else "degraded",
        version=__version__,
        torch=_version("torch"),
        torch_geometric=_version("torch_geometric"),
        models_loaded=sorted(reg.models),
        synthetic=reg.synthetic,
        auth_required=auth.required,
        problems=reg.problems,
        notes=reg.notes,
    )
