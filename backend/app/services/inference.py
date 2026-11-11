"""Suy luận GNN (P1-1).

Chưa làm: model đang huấn luyện trên Colab và notebook chưa có trong repo để port 1:1
`keep_nodes`, `cut_time`, `undirected` (BACKLOG O-1). Khi chưa có model, API trả 503 rõ ràng
thay vì một xác suất giả.
"""

from __future__ import annotations

from app.core.registry import Registry


class ModelUnavailable(RuntimeError):
    pass


def predict(
    reg: Registry, dataset: str, gid: int, feature: str, cutoff_h: float | None
) -> dict[str, object]:
    key = f"{dataset}_{feature}"
    if key not in reg.models:
        raise ModelUnavailable(
            f"Chưa có model cho {dataset} × {feature} (model đang huấn luyện, BACKLOG P1-1)."
        )
    raise ModelUnavailable("Suy luận chưa được cài đặt (BACKLOG P1-1).")


def model_ready(reg: Registry, dataset: str, feature: str) -> bool:
    return f"{dataset}_{feature}" in reg.models
