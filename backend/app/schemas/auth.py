from __future__ import annotations

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str = Field(min_length=1, max_length=64)
    password: str = Field(min_length=1, max_length=256)


class Me(BaseModel):
    username: str
    role: str
    auth_required: bool


class AdminStatus(BaseModel):
    artifacts_dir: str
    loaded_at: float
    synthetic: bool
    datasets: dict[str, int]
    tables: list[str]
    figures: int
    model_card: bool
    models_loaded: list[str]
    problems: list[str]
    notes: list[str]
