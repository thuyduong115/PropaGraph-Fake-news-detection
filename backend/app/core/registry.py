"""Nạp artifacts MỘT LẦN khi khởi động (AGENTS.md quy tắc 5).

Đã nạp: `model_card.json` (nếu có), `samples/<dataset>.json`, `tables/*.csv`, `results.csv`,
danh sách `figs/*.png`. Chưa nạp: model `.pt` và đồ thị `.pt` (P1-1, model đang huấn luyện).
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from app.services.results import Table, load_figures, load_tables
from app.services.samples import Graph, SampleFormatError, parse_samples

log = logging.getLogger(__name__)

DATASETS = ("politifact", "gossipcop")
FEATURES = ("profile", "bert")


@dataclass
class Registry:
    artifacts_dir: Path
    model_card: dict[str, Any] | None = None
    models: dict[str, Any] = field(default_factory=dict)
    graphs: dict[str, dict[int, Graph]] = field(default_factory=dict)
    tables: dict[str, Table] = field(default_factory=dict)
    figures: dict[str, Path] = field(default_factory=dict)
    synthetic: bool = False
    problems: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    loaded_at: float = 0.0

    @classmethod
    def load(cls, artifacts_dir: Path) -> Registry:
        reg = cls(artifacts_dir=artifacts_dir.resolve(), loaded_at=time.time())
        root = reg.artifacts_dir
        if not root.is_dir():
            reg.problems.append(f"Không thấy thư mục artifacts: {root}")
            log.warning(reg.problems[-1])
            return reg

        reg._load_model_card(root)
        reg._load_samples(root)
        reg.tables, table_problems = load_tables(root)
        reg.problems.extend(table_problems)
        reg.figures = load_figures(root)
        if not reg.models:
            reg.notes.append("Chưa nạp model GNN: dự đoán chưa khả dụng (BACKLOG P1-1).")
        for msg in reg.problems:
            log.warning(msg)
        return reg

    def _load_model_card(self, root: Path) -> None:
        path = root / "models" / "model_card.json"
        if not path.is_file():
            self.notes.append("Chưa có models/model_card.json (model đang huấn luyện).")
            return
        try:
            self.model_card = json.loads(path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            self.problems.append(f"models/model_card.json không hợp lệ: {exc}")

    @property
    def label_map(self) -> dict[str, Any] | None:
        card = self.model_card or {}
        lm = card.get("label_map")
        return lm if isinstance(lm, dict) else None

    def _load_samples(self, root: Path) -> None:
        for ds in DATASETS:
            rel = f"samples/{ds}.json"
            path = root / rel
            if not path.is_file():
                self.problems.append(f"Thiếu {rel}")
                continue
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
                graphs, synthetic = parse_samples(data, self.label_map, rel)
            except (json.JSONDecodeError, UnicodeDecodeError, SampleFormatError) as exc:
                self.problems.append(f"{rel} không hợp lệ: {exc}")
                continue
            self.graphs[ds] = {g.gid: g for g in graphs}
            self.synthetic = self.synthetic or synthetic

    @property
    def ready(self) -> bool:
        """Dữ liệu demo đã nạp đủ, không lỗi. Thiếu model chỉ là ghi chú, không phải lỗi."""
        return not self.problems
