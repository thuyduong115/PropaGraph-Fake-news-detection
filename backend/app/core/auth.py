"""Đăng nhập tối giản cho hệ thống minh họa (docs/accounts.md).

- Hai tài khoản cấu hình qua biến môi trường: `admin` (vai trò admin) và `user` (vai trò user).
- Không có bảng người dùng hay cơ sở dữ liệu; phiên là cookie httpOnly ký HMAC-SHA256.
- `AUTH_REQUIRED=0` tắt đăng nhập (mọi người xem như vai trò user).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from dataclasses import dataclass
from typing import Literal

from app.core.config import Settings

log = logging.getLogger(__name__)

COOKIE_NAME = "propagraph_session"
Role = Literal["admin", "user"]


@dataclass(frozen=True)
class Principal:
    username: str
    role: Role


ANONYMOUS = Principal(username="anonymous", role="user")


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    return base64.urlsafe_b64decode(text + "=" * (-len(text) % 4))


class Authenticator:
    def __init__(self, settings: Settings) -> None:
        self.required = settings.auth_required
        self.session_seconds = settings.session_hours * 3600
        secret = settings.auth_secret
        if not secret:
            secret = secrets.token_urlsafe(32)
            log.warning("AUTH_SECRET trống: dùng khoá ngẫu nhiên, phiên mất khi khởi động lại.")
        self._key = secret.encode()
        self._accounts: dict[str, tuple[str, Role]] = {}
        for username, password, role in (
            (settings.admin_username, settings.admin_password, "admin"),
            (settings.user_username, settings.user_password, "user"),
        ):
            if username and password:
                self._accounts[username] = (password, role)

    def verify(self, username: str, password: str) -> Principal | None:
        account = self._accounts.get(username)
        # so sánh hằng thời gian kể cả khi sai tên đăng nhập
        expected = account[0] if account else secrets.token_urlsafe(16)
        ok = hmac.compare_digest(password.encode(), expected.encode())
        return Principal(username, account[1]) if (account and ok) else None

    def issue(self, principal: Principal, now: float | None = None) -> str:
        payload = {
            "u": principal.username,
            "r": principal.role,
            "exp": int((now or time.time()) + self.session_seconds),
        }
        body = _b64(json.dumps(payload, separators=(",", ":")).encode())
        sig = _b64(hmac.new(self._key, body.encode(), hashlib.sha256).digest())
        return f"{body}.{sig}"

    def read(self, token: str | None, now: float | None = None) -> Principal | None:
        if not token or "." not in token:
            return None
        body, sig = token.rsplit(".", 1)
        expected = _b64(hmac.new(self._key, body.encode(), hashlib.sha256).digest())
        if not hmac.compare_digest(sig, expected):
            return None
        try:
            payload = json.loads(_unb64(body))
        except (ValueError, json.JSONDecodeError):
            return None
        if payload.get("exp", 0) < (now or time.time()):
            return None
        username, role = payload.get("u"), payload.get("r")
        # tài khoản bị đổi/xoá trong cấu hình thì phiên cũ hết hiệu lực
        account = self._accounts.get(username)
        if account is None or account[1] != role:
            return None
        return Principal(username, role)
