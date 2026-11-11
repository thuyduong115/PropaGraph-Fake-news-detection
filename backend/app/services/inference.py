"""Nạp model GNN + đồ thị demo và suy luận (P1-1).

Tương ứng notebook `notebooks/DACN2_v2.ipynb`:
- §3, ô `MODEL_SRC` / `predict`: class `GNN` (xuất thành `models/gnn_model.py`), xác suất lớp 1
  là `softmax(out)[:, 1]`.
- §10: nạp lại model từ export (`GNN(conv, in_dim, concat_root=True, variant='base')`,
  `load_state_dict(ck['model'])`), đồ thị demo lưu `x` float16 nên đổi lại float32 trước khi
  suy luận, golden = `undirected(g if cutoff is None else cut_time(g, cutoff))`.

torch / torch_geometric chỉ được import khi nạp model, nên backend vẫn chạy (không có dự đoán)
trên máy chưa cài hai thư viện này.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.core.registry import Registry


class ModelUnavailable(RuntimeError):
    pass


@dataclass
class LoadedModel:
    key: str  # "<dataset>_<feature>"
    file: str  # tên file .pt trong model card
    conv: str
    module: Any  # torch.nn.Module ở chế độ eval
    graphs: dict[int, Any]  # gid -> torch_geometric.data.Data (x float32)


def _load_gnn_class(path: Path) -> type:
    """Notebook §10: `exec(gnn_model.py)` rồi lấy `GNN`."""
    ns: dict[str, Any] = {}
    exec(compile(path.read_text(encoding="utf-8"), str(path), "exec"), ns)  # noqa: S102
    if "GNN" not in ns:
        raise ValueError("models/gnn_model.py không định nghĩa class GNN")
    return ns["GNN"]


def load_models(
    root: Path, entries: list[dict[str, Any]], device: str = "cpu"
) -> tuple[dict[str, LoadedModel], list[str]]:
    """Nạp mọi model trong model card và đồ thị demo tương ứng. Trả (models, lỗi)."""
    import torch

    problems: list[str] = []
    models: dict[str, LoadedModel] = {}
    try:
        gnn_cls = _load_gnn_class(root / "models" / "gnn_model.py")
    except (OSError, SyntaxError, ValueError, ImportError) as exc:
        return models, [f"Không nạp được models/gnn_model.py: {exc}"]

    graph_cache: dict[str, dict[int, Any]] = {}
    for e in entries:
        ds, feat, file = e.get("dataset"), e.get("feature"), e.get("file")
        key = f"{ds}_{feat}"
        try:
            ck = torch.load(root / "models" / str(file), map_location=device, weights_only=False)
            m = gnn_cls(e["conv"], int(e["in_dim"]), concat_root=True, variant="base")
            m.load_state_dict(ck["model"])
            m.to(device).eval()
            rel = f"graphs/{key}_demo.pt"
            if rel not in graph_cache:
                gs = torch.load(root / rel, map_location="cpu", weights_only=False)
                for g in gs:
                    g.x = g.x.float()
                graph_cache[rel] = {int(g.gid): g for g in gs}
        except Exception as exc:  # noqa: BLE001 — báo đúng lỗi trong health, không làm sập app
            problems.append(f"Không nạp được model {key} ({file}): {exc}")
            continue
        models[key] = LoadedModel(
            key=key, file=str(file), conv=str(e["conv"]), module=m, graphs=graph_cache[rel]
        )
    return models, problems


def model_ready(reg: Registry, dataset: str, feature: str) -> bool:
    return f"{dataset}_{feature}" in reg.models


def _get(reg: Registry, dataset: str, feature: str, gid: int) -> tuple[LoadedModel, Any]:
    lm = reg.models.get(f"{dataset}_{feature}")
    if lm is None:
        raise ModelUnavailable(f"Chưa nạp model cho {dataset} × {feature}.")
    g = lm.graphs.get(gid)
    if g is None:
        raise ModelUnavailable(f"Đồ thị {gid} không có trong graphs/{dataset}_{feature}_demo.pt.")
    return lm, g


FAKE = "fake"


def _class_index(reg: Registry, name: str) -> int:
    """Chỉ số lớp mang nhãn `name` theo `label_map` (AGENTS.md quy tắc 6)."""
    for k, v in (reg.label_map or {}).items():
        if str(v) == name:
            return int(k)
    raise ModelUnavailable(f"label_map trong model_card.json không có nhãn '{name}'.")


def probs(
    reg: Registry, dataset: str, feature: str, gid: int, cutoffs: list[float | None]
) -> list[tuple[float, int]]:
    """Xác suất nhãn `fake` và số node model thấy, cho từng mốc. Một lần forward cho mọi mốc."""
    import torch
    from torch_geometric.data import Batch

    from app.services.graph_ops import prepare

    lm, g = _get(reg, dataset, feature, gid)
    fake = _class_index(reg, FAKE)
    graphs = [prepare(g, c) for c in cutoffs]
    # `keep_nodes` gán num_nodes tường minh, đồ thị không cắt thì không: gán cho mọi đồ thị để
    # gộp được nhiều mốc vào một Batch (notebook gộp từng mốc riêng; kết quả như nhau).
    for gi in graphs:
        gi.num_nodes = gi.num_nodes
    device = next(lm.module.parameters()).device
    with torch.no_grad():
        p = lm.module(Batch.from_data_list(graphs).to(device)).softmax(1)[:, fake].cpu()
    return [(float(pi), int(gi.num_nodes)) for pi, gi in zip(p, graphs, strict=True)]


def predict(
    reg: Registry, dataset: str, gid: int, feature: str, cutoff_h: float | None
) -> dict[str, object]:
    lm, g = _get(reg, dataset, feature, gid)
    ((prob, n_used),) = probs(reg, dataset, feature, gid, [cutoff_h])
    # Notebook đánh giá bằng `p > .5` (2 lớp); tên nhãn lấy từ label_map (quy tắc 6).
    other = [str(v) for v in (reg.label_map or {}).values() if str(v) != FAKE]
    pred = FAKE if prob > 0.5 else (other[0] if len(other) == 1 else "not-" + FAKE)
    return {
        "prob_fake": prob,
        "pred_label": pred,
        "n_nodes_used": n_used,
        "n_nodes_total": int(g.num_nodes),
        "model": lm.file,
    }
