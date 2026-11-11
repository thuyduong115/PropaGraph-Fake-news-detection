from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Health(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    artifacts_dir: str
    torch: str | None
    torch_geometric: str | None
    models_loaded: list[str]
    problems: list[str]
