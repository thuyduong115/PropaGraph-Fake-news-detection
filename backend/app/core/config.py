"""Cấu hình đọc từ biến môi trường hoặc .env (xem .env.example)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    # .env ở gốc repo khi chạy từ backend/, hoặc .env cạnh nơi chạy
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    artifacts_dir: Path = Path("artifacts")
    device: str = "cpu"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [o.strip() for o in value.split(",") if o.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
