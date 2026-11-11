from __future__ import annotations

from fastapi.testclient import TestClient


def test_tables_listed_with_groups_and_row_counts(client: TestClient) -> None:
    tables = {t["name"]: t for t in client.get("/api/results/tables").json()}
    assert tables["E0_main"] == {"name": "E0_main", "group": "experiment", "n_rows": 2}
    assert tables["R1_labels"]["group"] == "reliability"
    assert tables["results"]["group"] == "summary"
    assert tables["ALL_summary"]["group"] == "summary"
    assert tables["graph_meta"]["group"] == "meta"
    only = client.get("/api/results/tables", params={"group": "experiment"}).json()
    assert [t["name"] for t in only] == ["E0_main"]


def test_table_values_are_verbatim_strings(client: TestClient) -> None:
    body = client.get("/api/results/tables/E0_main").json()
    assert body["columns"] == ["a", "b"]
    assert body["rows"] == [["1", "2"], ["3", "4"]]
    assert client.get("/api/results/tables/khong-co").status_code == 404


def test_figures(client: TestClient) -> None:
    figs = client.get("/api/results/figures").json()
    assert figs == [{"name": "fake", "url": "/api/results/figures/fake"}]
    resp = client.get("/api/results/figures/fake")
    assert resp.status_code == 200 and resp.headers["content-type"] == "image/png"
    assert client.get("/api/results/figures/..%2Fresults").status_code == 404
