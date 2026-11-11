from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import create_app
from tests.conftest import FAKE_CARD, USER, login, make_settings


def test_health_ok_with_artifacts(anon: TestClient) -> None:
    body = anon.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["problems"] == []
    assert body["auth_required"] is True
    assert "artifacts_dir" not in body  # không lộ đường dẫn máy chủ khi chưa đăng nhập


def test_health_degraded_without_artifacts(tmp_path: Path) -> None:
    with TestClient(create_app(make_settings(tmp_path / "khong-co"))) as c:
        body = c.get("/api/health").json()
    assert body["status"] == "degraded"
    assert any("artifacts" in p for p in body["problems"])


def test_models_returns_card_verbatim(client: TestClient) -> None:
    resp = client.get("/api/models")
    assert resp.status_code == 200
    assert resp.json() == FAKE_CARD


def test_models_503_without_card(tmp_path: Path) -> None:
    with TestClient(create_app(make_settings(tmp_path))) as c:
        login(c, USER)
        assert c.get("/api/models").status_code == 503


def test_openapi_lists_routes(anon: TestClient) -> None:
    paths = set(anon.get("/openapi.json").json()["paths"])
    expected = {
        "/api/health",
        "/api/models",
        "/api/datasets",
        "/api/datasets/{ds}/graphs",
        "/api/datasets/{ds}/graphs/{gid}",
        "/api/datasets/{ds}/graphs/{gid}/timeline",
        "/api/predict",
        "/api/results/tables",
        "/api/results/tables/{name}",
        "/api/results/figures",
        "/api/results/figures/{name}",
        "/api/auth/login",
        "/api/auth/me",
        "/api/admin/status",
    }
    assert expected <= paths


def test_cors_origins_from_comma_string(tmp_path: Path) -> None:
    s = make_settings(tmp_path, cors_origins="http://a.test, http://b.test")
    assert s.cors_origins == ["http://a.test", "http://b.test"]


def test_relative_artifacts_dir_resolves_from_repo_root() -> None:
    s = make_settings(Path("artifacts"))
    assert s.artifacts_path == Path(__file__).resolve().parents[2] / "artifacts"
