"""Đọc bảng kết quả (`tables/*.csv`, `results.csv`) và hình (`figs/*.png`).

Giá trị giữ nguyên chuỗi như notebook xuất: không làm tròn, không tính lại (AGENTS.md quy tắc 2).
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

# Theo tên notebook §9–§10 xuất (docs/open_questions.md #9): `E<số>_*` → thực nghiệm,
# `results` và `ALL_*` (bảng tổng hợp §9.3) → tổng hợp, cả hai lên trang Results;
# `graph_meta` → meta; còn lại (`reliability_*`…) → DataReliability.
_EXPERIMENT = re.compile(r"^E\d", re.IGNORECASE)
_SUMMARY = re.compile(r"^ALL_", re.IGNORECASE)
_NAME = re.compile(r"^[A-Za-z0-9_.-]+$")


@dataclass
class Table:
    name: str
    group: str  # "experiment" | "reliability" | "summary" | "meta"
    columns: list[str]
    rows: list[list[str]]


def table_group(name: str) -> str:
    if name == "results" or _SUMMARY.match(name):
        return "summary"
    if name == "graph_meta":
        return "meta"
    return "experiment" if _EXPERIMENT.match(name) else "reliability"


def read_csv(path: Path, name: str) -> Table:
    with path.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        columns = next(reader, [])
        rows = [row for row in reader if row]
    return Table(name=name, group=table_group(name), columns=columns, rows=rows)


def load_tables(root: Path) -> tuple[dict[str, Table], list[str]]:
    tables: dict[str, Table] = {}
    problems: list[str] = []
    paths = sorted((root / "tables").glob("*.csv"))
    if (root / "results.csv").is_file():
        paths.append(root / "results.csv")
    for path in paths:
        name = path.stem
        if not _NAME.match(name):
            problems.append(f"Bỏ qua bảng có tên không hợp lệ: {path.name}")
            continue
        try:
            tables[name] = read_csv(path, name)
        except (OSError, UnicodeDecodeError, csv.Error) as exc:
            problems.append(f"Không đọc được {path.name}: {exc}")
    return tables, problems


def load_figures(root: Path) -> dict[str, Path]:
    return {
        p.stem: p.resolve() for p in sorted((root / "figs").glob("*.png")) if _NAME.match(p.stem)
    }
