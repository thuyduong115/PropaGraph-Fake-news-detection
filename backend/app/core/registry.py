"""Nạp artifacts MỘT LẦN khi khởi động (AGENTS.md quy tắc 5).

P0: mới nạp `models/model_card.json`. Model `.pt`, đồ thị demo và samples nạp ở P1-1, sau khi
có notebook để port `graph_ops` (BACKLOG O-1).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

log = logging.getLogger(__name__)


@dataclass
class Registry:
    artifacts_dir: Path
    model_card: dict[str, Any] | None = None
    models: dict[str, Any] = field(default_factory=dict)
    problems: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, artifacts_dir: Path) -> Registry:
        reg = cls(artifacts_dir=artifacts_dir.resolve())
        if not reg.artifacts_dir.is_dir():
            reg.problems.append(f"Không thấy thư mục artifacts: {reg.artifacts_dir}")
            log.warning(reg.problems[-1])
            return reg

        card_path = reg.artifacts_dir / "models" / "model_card.json"
        try:
            reg.model_card = json.loads(card_path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            reg.problems.append("Thiếu models/model_card.json")
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            reg.problems.append(f"models/model_card.json không hợp lệ: {exc}")
        for msg in reg.problems:
            log.warning(msg)
        return reg

    @property
    def ready(self) -> bool:
        return not self.problems
