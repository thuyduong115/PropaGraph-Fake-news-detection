from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app
from tests.conftest import FAKE_CARD


def test_health_ok_with_artifacts(client: TestClient) -> None:
    body = client.get("/api/health").json()
    assert body["status"] == "ok"
    assert body["problems"] == []


def test_health_degraded_without_artifacts(tmp_path: Path) -> None:
    app = create_app(Settings(artifacts_dir=tmp_path / "khong-co"))
    with TestClient(app) as c:
        body = c.get("/api/health").json()
    assert body["status"] == "degraded"
    assert any("artifacts" in p for p in body["problems"])


def test_models_returns_card_verbatim(client: TestClient) -> None:
    resp = client.get("/api/models")
    assert resp.status_code == 200
    assert resp.json() == FAKE_CARD


def test_models_503_without_card(tmp_path: Path) -> None:
    with TestClient(create_app(Settings(artifacts_dir=tmp_path))) as c:
        assert c.get("/api/models").status_code == 503


def test_openapi_lists_routes(client: TestClient) -> None:
    paths = client.get("/openapi.json").json()["paths"]
    assert {"/api/health", "/api/models"} <= set(paths)


def test_cors_origins_from_comma_string() -> None:
    s = Settings(cors_origins="http://a.test, http://b.test")
    assert s.cors_origins == ["http://a.test", "http://b.test"]
