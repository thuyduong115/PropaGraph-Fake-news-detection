"""Cấu hình đọc từ biến môi trường hoặc .env (xem .env.example)."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Annotated

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

# backend/app/core/config.py → gốc repo
REPO_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    # .env ở gốc repo khi chạy từ backend/, hoặc .env cạnh nơi chạy
    model_config = SettingsConfigDict(env_file=("../.env", ".env"), extra="ignore")

    artifacts_dir: Path = Path("artifacts")
    device: str = "cpu"
    cors_origins: Annotated[list[str], NoDecode] = ["http://localhost:5173"]

    # Đăng nhập (docs/accounts.md). Mật khẩu mặc định chỉ dùng khi phát triển/demo.
    auth_required: bool = True
    auth_secret: str = ""
    session_hours: int = 12
    cookie_secure: bool = False
    admin_username: str = "admin"
    admin_password: str = "admin@123"
    user_username: str = "user"
    user_password: str = "user@123"

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [o.strip() for o in value.split(",") if o.strip()]
        return value

    @property
    def artifacts_path(self) -> Path:
        """Đường dẫn tương đối tính từ gốc repo, không phụ thuộc thư mục đang chạy."""
        p = self.artifacts_dir
        return p if p.is_absolute() else (REPO_ROOT / p)


@lru_cache
def get_settings() -> Settings:
    return Settings()
