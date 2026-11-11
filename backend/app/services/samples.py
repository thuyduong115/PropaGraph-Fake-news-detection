"""Đọc `samples/<dataset>.json` (cây lan truyền dạng JSON nhẹ, docs/development.md §2).

Định dạng mong đợi ghi ở `docs/api.md` mục "Định dạng samples". Các phép tính ở đây chỉ là
thống kê cấu trúc (đếm node, độ sâu, khoảng thời gian), không phải số liệu thực nghiệm.
Phép cắt cây cho suy luận (`keep_nodes`, `cut_time`) nằm ở `graph_ops.py`, port 1:1 từ notebook.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

# Mốc thời gian (giờ) của thanh trượt; None = toàn bộ cây (docs/development.md §4).
TIMELINE: tuple[float | None, ...] = (0.5, 1, 3, 6, 12, 24, 72, 168, None)


class SampleFormatError(ValueError):
    pass


@dataclass
class Graph:
    gid: int
    news_id: str | None
    title: str | None
    label: str | None
    nodes: list[dict[str, Any]]
    edges: list[list[int]]
    n_nodes: int = 0
    depth: int = 0
    span_h: float | None = None
    growth: list[int] = field(default_factory=list)

    def summary(self) -> dict[str, Any]:
        return {
            "gid": self.gid,
            "news_id": self.news_id,
            "title": self.title,
            "label": self.label,
            "n_nodes": self.n_nodes,
            "depth": self.depth,
            "span_h": self.span_h,
            "growth": self.growth,
        }


def observed_count(nodes: list[dict[str, Any]], cutoff_h: float | None) -> int:
    """Số node nhìn thấy tại mốc `cutoff_h`: gốc + node có `t_rel_h <= cutoff_h`.

    Chỉ dùng để hiển thị (đếm, làm mờ). Node mất cha được nối lại vào gốc khi suy luận, nên
    số node không đổi theo cách nối.
    """
    if cutoff_h is None:
        return len(nodes)
    return sum(
        1
        for n in nodes
        if n["depth"] == 0 or (n["t_rel_h"] is not None and n["t_rel_h"] <= cutoff_h)
    )


def map_label(raw: Any, label_map: dict[str, Any] | None) -> str | None:
    """Nhãn chữ theo `label_map` của model card; không tự gán nghĩa cho 0/1 (AGENTS.md, 6)."""
    if raw is None:
        return None
    if label_map and str(raw) in label_map:
        return str(label_map[str(raw)])
    return str(raw)


def _parse_node(raw: Any, where: str) -> dict[str, Any]:
    if not isinstance(raw, dict) or "id" not in raw:
        raise SampleFormatError(f"{where}: node phải là object có khoá id")
    t = raw.get("t_rel_h")
    return {
        "id": int(raw["id"]),
        "depth": int(raw.get("depth", 0)),
        "t_rel_h": None if t is None else float(t),
    }


def parse_graph(raw: Any, label_map: dict[str, Any] | None, where: str) -> Graph:
    if not isinstance(raw, dict) or "gid" not in raw:
        raise SampleFormatError(f"{where}: đồ thị phải là object có khoá gid")
    nodes = [_parse_node(n, f"{where}.nodes") for n in raw.get("nodes", [])]
    if not nodes:
        raise SampleFormatError(f"{where}: đồ thị gid={raw['gid']} không có node")
    ids = {n["id"] for n in nodes}
    edges: list[list[int]] = []
    for e in raw.get("edges", []):
        if not isinstance(e, list | tuple) or len(e) != 2:
            raise SampleFormatError(f"{where}: cạnh phải là [src, dst]")
        src, dst = int(e[0]), int(e[1])
        if src not in ids or dst not in ids:
            raise SampleFormatError(f"{where}: cạnh {e} trỏ tới node không tồn tại")
        edges.append([src, dst])

    times = [n["t_rel_h"] for n in nodes if n["t_rel_h"] is not None]
    g = Graph(
        gid=int(raw["gid"]),
        news_id=None if raw.get("news_id") is None else str(raw["news_id"]),
        title=raw.get("title"),
        label=map_label(raw.get("label"), label_map),
        nodes=nodes,
        edges=edges,
    )
    g.n_nodes = len(nodes)
    g.depth = max(n["depth"] for n in nodes)
    g.span_h = max(times) if times else None
    g.growth = [observed_count(nodes, c) for c in TIMELINE]
    return g


def parse_samples(
    data: Any, label_map: dict[str, Any] | None, where: str
) -> tuple[list[Graph], bool]:
    """Trả (danh sách đồ thị, cờ synthetic). Nhận `{"graphs": [...]}` hoặc danh sách trực tiếp."""
    synthetic = False
    if isinstance(data, dict):
        synthetic = bool(data.get("synthetic", False))
        data = data.get("graphs")
    if not isinstance(data, list):
        raise SampleFormatError(f"{where}: cần danh sách đồ thị hoặc object có khoá graphs")
    graphs = [parse_graph(g, label_map, f"{where}[{i}]") for i, g in enumerate(data)]
    gids = [g.gid for g in graphs]
    if len(set(gids)) != len(gids):
        raise SampleFormatError(f"{where}: gid bị trùng")
    return graphs, synthetic
