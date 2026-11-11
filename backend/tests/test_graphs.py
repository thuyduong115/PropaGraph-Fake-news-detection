from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.services.samples import SampleFormatError, observed_count, parse_samples


def test_datasets_lists_counts_and_mapped_labels(client: TestClient) -> None:
    body = client.get("/api/datasets").json()
    assert [d["name"] for d in body] == ["politifact", "gossipcop"]
    # nhãn đi qua label_map của model card, không tự gán nghĩa 0/1
    assert body[0] == {"name": "politifact", "n_graphs": 3, "labels": ["nhan-a", "nhan-b"]}


def test_unknown_dataset_404(client: TestClient) -> None:
    assert client.get("/api/datasets/twitter/graphs").status_code == 404


def test_list_filters_and_paging(client: TestClient) -> None:
    url = "/api/datasets/gossipcop/graphs"
    assert client.get(url).json()["total"] == 3
    assert client.get(url, params={"label": "nhan-b"}).json()["total"] == 2
    assert client.get(url, params={"min_nodes": 3, "max_nodes": 4}).json()["total"] == 1
    assert [g["gid"] for g in client.get(url, params={"q": "ALPHA"}).json()["items"]] == [0, 2]
    page = client.get(url, params={"size": 2, "page": 2, "sort": "-n_nodes"}).json()
    assert [g["gid"] for g in page["items"]] == [2]


def test_summary_fields(client: TestClient) -> None:
    g = client.get("/api/datasets/politifact/graphs", params={"q": "Beta"}).json()["items"][0]
    assert (g["n_nodes"], g["depth"], g["span_h"]) == (6, 1, 200.0)
    # mốc 0.5h: gốc + 0.1 + 0.4 ; toàn bộ: 6
    assert g["growth"][0] == 3 and g["growth"][-1] == 6


def test_detail_and_404(client: TestClient) -> None:
    body = client.get("/api/datasets/politifact/graphs/1").json()
    assert len(body["nodes"]) == 6 and len(body["edges"]) == 5
    assert body["nodes"][0] == {"id": 0, "depth": 0, "t_rel_h": 0.0}
    assert client.get("/api/datasets/politifact/graphs/99").status_code == 404


def test_timeline_without_model(client: TestClient) -> None:
    body = client.get("/api/datasets/politifact/graphs/1/timeline?feature=profile").json()
    assert body["model_ready"] is False
    assert [p["cutoff_h"] for p in body["points"]][-1] is None
    assert [p["n_nodes_used"] for p in body["points"]] == [3, 4, 4, 5, 5, 5, 5, 5, 6]
    assert all(p["prob_fake"] is None for p in body["points"])


def test_predict_503_until_model_ready(client: TestClient) -> None:
    body = {"dataset": "politifact", "gid": 1, "feature": "bert", "cutoff_h": None}
    resp = client.post("/api/predict", json=body)
    assert resp.status_code == 503
    assert "huấn luyện" in resp.json()["detail"]
    assert client.post("/api/predict", json={**body, "gid": 99}).status_code == 404
    assert client.post("/api/predict", json={**body, "feature": "spacy"}).status_code == 422


def test_observed_count_keeps_root() -> None:
    nodes = [
        {"id": 0, "depth": 0, "t_rel_h": None},
        {"id": 1, "depth": 1, "t_rel_h": 2.0},
    ]
    assert observed_count(nodes, 1.0) == 1
    assert observed_count(nodes, None) == 2


def test_bad_samples_rejected() -> None:
    with pytest.raises(SampleFormatError):
        parse_samples({"graphs": [{"gid": 1, "nodes": []}]}, None, "x")
    with pytest.raises(SampleFormatError):
        parse_samples(
            [{"gid": 1, "nodes": [{"id": 0}], "edges": [[0, 5]]}],
            None,
            "x",
        )
    dup = {"gid": 1, "nodes": [{"id": 0}]}
    with pytest.raises(SampleFormatError):
        parse_samples([dup, dup], None, "x")


def test_synthetic_flag(client: TestClient) -> None:
    graphs, synthetic = parse_samples({"synthetic": True, "graphs": []}, None, "x")
    assert synthetic is True and graphs == []
