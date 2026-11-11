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
FAKE_CARD = {"label_map": {"0": "fake-label-a", "1": "fake-label-b"}, "note": "fixture giả"}


def make_fake_artifacts(root: Path, card: dict | None = None) -> Path:
    """Tạo đủ cây thư mục artifacts theo README §2, nội dung rỗng/giả."""
    for sub in ("models", "graphs", "samples", "tables", "figs"):
        (root / sub).mkdir(parents=True, exist_ok=True)
    (root / "models/model_card.json").write_text(json.dumps(card or FAKE_CARD), encoding="utf-8")
    (root / "models/gnn_model.py").write_text("# giả\n", encoding="utf-8")
    (root / "models/golden_predictions.json").write_text("[]", encoding="utf-8")
    (root / "results.csv").write_text("col\n", encoding="utf-8")
    (root / "tables/graph_meta.csv").write_text("gid\n", encoding="utf-8")
    (root / "figs/fake.png").write_bytes(b"")
    for ds in DATASETS:
        (root / f"samples/{ds}.json").write_text("[]", encoding="utf-8")
        for feat in FEATURES:
            (root / f"graphs/{ds}_{feat}_demo.pt").write_bytes(b"")
            (root / f"models/{ds}_{feat}_fakeconv.pt").write_bytes(b"")
    return root


@pytest.fixture
def fake_artifacts(tmp_path: Path) -> Path:
    return make_fake_artifacts(tmp_path / "artifacts")


@pytest.fixture
def client(fake_artifacts: Path) -> Iterator[TestClient]:
    with TestClient(create_app(Settings(artifacts_dir=fake_artifacts))) as c:
        yield c
