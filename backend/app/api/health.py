from __future__ import annotations

import importlib.metadata
from typing import Annotated

from fastapi import APIRouter, Depends

from app import __version__
from app.api.deps import get_registry
from app.core.registry import Registry
from app.schemas.health import Health

router = APIRouter(tags=["health"])


def _version(dist: str) -> str | None:
    try:
        return importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError:
        return None


@router.get("/health", response_model=Health)
def health(reg: Annotated[Registry, Depends(get_registry)]) -> Health:
    """Báo đúng tình trạng: thiếu artifacts thì `degraded` kèm danh sách vấn đề."""
    return Health(
        status="ok" if reg.ready else "degraded",
        version=__version__,
        artifacts_dir=str(reg.artifacts_dir),
        torch=_version("torch"),
        torch_geometric=_version("torch_geometric"),
        models_loaded=sorted(reg.models),
        problems=reg.problems,
    )
