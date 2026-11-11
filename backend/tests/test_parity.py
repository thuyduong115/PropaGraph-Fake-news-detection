"""Parity: backend tái tạo đúng xác suất notebook (AGENTS.md quy tắc 3, BACKLOG P1-1).

So với `artifacts/models/golden_predictions.json` do notebook §10 sinh ra: với mỗi model, 20 đồ
thị demo đầu tiên × mốc cắt {1 giờ, 24 giờ, toàn bộ}, sai số xác suất ≤ 1e-4 và số node khớp
tuyệt đối. Cần artifacts thật và torch / torch_geometric; thiếu thì skip kèm lý do.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.core.config import REPO_ROOT, get_settings

pytest.importorskip("torch", reason="chưa cài torch (xem model_card.json)")
pytest.importorskip("torch_geometric", reason="chưa cài torch_geometric (xem model_card.json)")

from app.core.registry import Registry  # noqa: E402
from app.services import inference  # noqa: E402
from app.services.samples import observed_count  # noqa: E402

TOL = 1e-4


def _artifacts() -> Path:
    try:
        return get_settings().artifacts_path
    except Exception:  # noqa: BLE001
        return REPO_ROOT / "artifacts"


GOLDEN = _artifacts() / "models" / "golden_predictions.json"
pytestmark = pytest.mark.skipif(
    not GOLDEN.is_file(), reason=f"thiếu {GOLDEN} (copy export/ từ Drive về artifacts/)"
)


@pytest.fixture(scope="module")
def reg() -> Registry:
    r = Registry.load(_artifacts())
    assert r.models, f"không nạp được model: {r.problems}"
    return r


@pytest.fixture(scope="module")
def golden() -> dict:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def _key_of(reg: Registry, file: str) -> tuple[str, str]:
    for e in reg.card_entries:
        if e.get("file") == file:
            return e["dataset"], e["feature"]
    raise AssertionError(f"{file} không có trong model_card.json")


def test_all_card_models_loaded(reg: Registry) -> None:
    assert reg.problems == []
    assert len(reg.models) == len(reg.card_entries)


def test_golden_probabilities(reg: Registry, golden: dict) -> None:
    worst = 0.0
    for case in golden["cases"]:
        ds, feat = _key_of(reg, case["model"])
        ((p, n_used),) = inference.probs(reg, ds, feat, case["gid"], [case["cutoff_h"]])
        assert n_used == case["n_nodes"], case
        worst = max(worst, abs(p - case["prob_fake"]))
        assert abs(p - case["prob_fake"]) <= TOL, (case, p)
    print(f"{len(golden['cases'])} ca, sai số lớn nhất {worst:.2e}")


def test_samples_count_matches_model_input(reg: Registry, golden: dict) -> None:
    """Số node hiển thị theo `t_rel_h` (samples) = số node model thấy theo `rt` (.pt)
    (docs/open_questions.md #10)."""
    for case in golden["cases"]:
        ds, _ = _key_of(reg, case["model"])
        g = reg.graphs[ds][case["gid"]]
        assert observed_count(g.nodes, case["cutoff_h"]) == case["n_nodes"], case


def test_api_timeline_and_predict_agree(reg: Registry) -> None:
    """Qua API thật: xác suất ở mốc cuối của timeline = /api/predict với cutoff null."""
    from fastapi.testclient import TestClient

    from app.main import create_app
    from tests.conftest import USER, login, make_settings

    with TestClient(create_app(make_settings(_artifacts()))) as c:
        login(c, USER)
        assert c.get("/api/health").json()["status"] == "ok"
        for e in reg.card_entries:
            ds, feat = e["dataset"], e["feature"]
            gid = next(iter(reg.graphs[ds]))
            tl = c.get(f"/api/datasets/{ds}/graphs/{gid}/timeline", params={"feature": feat})
            assert tl.status_code == 200 and tl.json()["model_ready"]
            last = tl.json()["points"][-1]
            body = {"dataset": ds, "gid": gid, "feature": feat, "cutoff_h": None}
            pr = c.post("/api/predict", json=body).json()
            assert abs(pr["prob_fake"] - last["prob_fake"]) <= TOL
            assert pr["n_nodes_used"] == last["n_nodes_used"] == pr["n_nodes_total"]
            assert pr["model"] == e["file"]
            assert pr["pred_label"] in set(reg.label_map.values())
