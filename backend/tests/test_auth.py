from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.auth import Authenticator, Principal
from app.main import create_app
from tests.conftest import ADMIN, USER, make_settings


def test_protected_routes_need_login(anon: TestClient) -> None:
    for path in ("/api/datasets", "/api/results/tables", "/api/models", "/api/auth/me"):
        assert anon.get(path).status_code == 401, path


def test_wrong_password_rejected(anon: TestClient) -> None:
    resp = anon.post("/api/auth/login", json={"username": USER[0], "password": "sai"})
    assert resp.status_code == 401
    resp = anon.post("/api/auth/login", json={"username": "khong-co", "password": "x"})
    assert resp.status_code == 401


def test_login_sets_httponly_cookie_and_me(anon: TestClient) -> None:
    resp = anon.post("/api/auth/login", json={"username": USER[0], "password": USER[1]})
    assert "httponly" in resp.headers["set-cookie"].lower()
    me = anon.get("/api/auth/me").json()
    assert me == {"username": USER[0], "role": "user", "auth_required": True}


def test_logout_clears_session(client: TestClient) -> None:
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_user_cannot_use_admin(client: TestClient) -> None:
    assert client.get("/api/admin/status").status_code == 403
    assert client.post("/api/admin/reload").status_code == 403


def test_admin_status_and_reload(admin: TestClient) -> None:
    status = admin.get("/api/admin/status").json()
    assert status["datasets"] == {"politifact": 3, "gossipcop": 3}
    assert status["model_card"] is True
    assert admin.post("/api/admin/reload").status_code == 200


def test_auth_can_be_disabled(fake_artifacts: Path) -> None:
    with TestClient(create_app(make_settings(fake_artifacts, auth_required=False))) as c:
        assert c.get("/api/datasets").status_code == 200
        assert c.get("/api/auth/me").json()["role"] == "user"
        assert c.get("/api/admin/status").status_code == 403


def test_token_tampering_and_expiry(tmp_path: Path) -> None:
    auth = Authenticator(make_settings(tmp_path))
    token = auth.issue(Principal(ADMIN[0], "admin"), now=1000.0)
    assert auth.read(token, now=1001.0) == Principal(ADMIN[0], "admin")
    assert auth.read(token, now=1000.0 + 13 * 3600) is None
    body, sig = token.rsplit(".", 1)
    assert auth.read(body + "." + sig[::-1], now=1001.0) is None
    other = Authenticator(make_settings(tmp_path, auth_secret="khac"))
    assert other.read(token, now=1001.0) is None


def test_role_change_invalidates_session(tmp_path: Path) -> None:
    token = Authenticator(make_settings(tmp_path)).issue(Principal(USER[0], "user"))
    renamed = Authenticator(make_settings(tmp_path, user_username="nguoi-khac"))
    assert renamed.read(token) is None
