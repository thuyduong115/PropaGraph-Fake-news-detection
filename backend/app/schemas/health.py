from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class Health(BaseModel):
    status: Literal["ok", "degraded"]
    version: str
    torch: str | None
    torch_geometric: str | None
    models_loaded: list[str]
    synthetic: bool
    auth_required: bool
    problems: list[str]
    notes: list[str]
