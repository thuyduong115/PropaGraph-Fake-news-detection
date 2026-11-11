"""Phép cắt cây cho suy luận, port 1:1 từ notebook (AGENTS.md quy tắc 3).

Nguồn: `notebooks/DACN2_v2.ipynb`, §3 "Lõi huấn luyện GNN" (ô định nghĩa `attach`,
`undirected`, `keep_nodes`, `cut_time`). Giữ nguyên thuật toán và thứ tự phép tính; chỉ thêm
chú thích kiểu và docstring. Sửa ở đây thì `tests/test_parity.py` phải còn xanh.

Đồ thị là `torch_geometric.data.Data` trong `graphs/<dataset>_<feature>_demo.pt`: node 0 là
gốc (bài báo), `rt` là thời gian tương đối theo giờ (gốc = 0), cạnh có hướng cha → con.
"""

from __future__ import annotations

import torch
from torch_geometric.data import Data
from torch_geometric.utils import to_undirected


def undirected(g: Data) -> Data:
    """Notebook `undirected`: model huấn luyện trên đồ thị vô hướng."""
    g = g.clone()
    if g.edge_index.numel():
        g.edge_index = to_undirected(g.edge_index, num_nodes=g.num_nodes)
    return g


def keep_nodes(g: Data, keep: torch.Tensor) -> Data:
    """Notebook `keep_nodes`: giữ tập node `keep` (luôn gồm gốc); node mất cha nối lại vào gốc."""
    keep = keep.clone()
    keep[0] = True
    old = torch.nonzero(keep).flatten()
    new_of = -torch.ones(g.num_nodes, dtype=torch.long)
    new_of[old] = torch.arange(len(old))
    src, dst = g.edge_index
    parent = torch.zeros(g.num_nodes, dtype=torch.long)
    parent[dst] = src
    kids = old[1:]
    par = parent[kids]
    par = torch.where(keep[par], par, torch.zeros_like(par))  # cha bị cắt -> nối vào gốc
    h = g.clone()
    h.x, h.rt = g.x[keep], g.rt[keep]
    h.edge_index = (
        torch.stack([new_of[par], new_of[kids]])
        if len(kids)
        else torch.empty(2, 0, dtype=torch.long)
    )
    h.num_nodes = len(old)
    return h


def cut_time(g: Data, hours: float) -> Data:
    """Notebook `cut_time`: giữ user có `rt <= hours` (rt NaN bị loại), rồi `keep_nodes`."""
    return keep_nodes(g, g.rt <= hours)


def prepare(g: Data, cutoff_h: float | None) -> Data:
    """Đồ thị đưa vào model, đúng như golden ở notebook §10:
    `undirected(g if cutoff is None else cut_time(g, cutoff))`."""
    return undirected(g if cutoff_h is None else cut_time(g, cutoff_h))
