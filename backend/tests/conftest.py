"""Fixture dùng chung. Artifacts ở đây là GIẢ, chỉ để kiểm tra cấu trúc; không chứa số liệu
thực nghiệm (AGENTS.md quy tắc 2)."""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings
from app.main import create_app

DATASETS = ("politifact", "gossipcop")
FEATURES = ("profile", "bert")
FAKE_CARD = {"label_map": {"0": "nhan-a", "1": "nhan-b"}, "note": "fixture giả"}
ADMIN = ("admin-test", "admin-pass")
USER = ("user-test", "user-pass")


def fake_graph(gid: int, label: object, title: str, times: list[float]) -> dict:
    """Cây sao: gốc 0 và các node con với thời gian `times`."""
    nodes = [{"id": 0, "depth": 0, "t_rel_h": 0.0}]
    nodes += [{"id": i + 1, "depth": 1, "t_rel_h": t} for i, t in enumerate(times)]
    edges = [[0, i + 1] for i in range(len(times))]
    return {
        "gid": gid,
        "news_id": f"n{gid}",
        "title": title,
        "label": label,
        "nodes": nodes,
        "edges": edges,
    }


SAMPLE_GRAPHS = [
    fake_graph(0, 0, "Alpha story", [0.2, 2.0, 30.0]),
    fake_graph(1, 1, "Beta story", [0.1, 0.4, 0.9, 5.0, 200.0]),
    fake_graph(2, 1, "Gamma alpha", [1.5]),
]


def make_fake_artifacts(root: Path, card: dict | list | None = None) -> Path:
    """Tạo đủ cây thư mục artifacts theo README §2, nội dung giả."""
    for sub in ("models", "graphs", "samples", "tables", "figs"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    (root / "models/model_card.json").write_text(json.dumps(card or FAKE_CARD), encoding="utf-8")
    (root / "models/gnn_model.py").write_text("# giả\n", encoding="utf-8")
    (root / "models/golden_predictions.json").write_text("[]", encoding="utf-8")
    (root / "results.csv").write_text("model,score\nX,0.5\n", encoding="utf-8")
    (root / "tables/graph_meta.csv").write_text("gid\n0\n", encoding="utf-8")
    (root / "tables/E0_main.csv").write_text("a,b\n1,2\n3,4\n", encoding="utf-8")
    (root / "tables/R1_labels.csv").write_text("finding\nx\n", encoding="utf-8")
    (root / "figs/fake.png").write_bytes(b"\x89PNG\r\n\x1a\n")
    for ds in DATASETS:
        payload = {"graphs": SAMPLE_GRAPHS}
        (root / f"samples/{ds}.json").write_text(json.dumps(payload), encoding="utf-8")
        for feat in FEATURES:
            (root / f"graphs/{ds}_{feat}_demo.pt").write_bytes(b"")
            (root / f"models/{ds}_{feat}_fakeconv.pt").write_bytes(b"")
    return root


def make_settings(artifacts: Path, **overrides) -> Settings:
    values = dict(
        artifacts_dir=artifacts,
        auth_secret="test-secret",
        admin_username=ADMIN[0],
        admin_password=ADMIN[1],
        user_username=USER[0],
        user_password=USER[1],
    )
    values.update(overrides)
    return Settings(**values)


def login(c: TestClient, account: tuple[str, str]) -> TestClient:
    resp = c.post("/api/auth/login", json={"username": account[0], "password": account[1]})
    assert resp.status_code == 200, resp.text
    return c


@pytest.fixture
def fake_artifacts(tmp_path: Path) -> Path:
    return make_fake_artifacts(tmp_path / "artifacts")


@pytest.fixture
def anon(fake_artifacts: Path) -> Iterator[TestClient]:
    with TestClient(create_app(make_settings(fake_artifacts))) as c:
        yield c


@pytest.fixture
def client(anon: TestClient) -> TestClient:
    """Đã đăng nhập vai trò user."""
    return login(anon, USER)


@pytest.fixture
def admin(anon: TestClient) -> TestClient:
    return login(anon, ADMIN)
