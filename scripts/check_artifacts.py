"""Kiểm tra thư mục artifacts/ trước khi chạy backend.

Xem docs/development.md §2 và DATA_BOUNDARY.md mục 3.

    python scripts/check_artifacts.py                     # đọc ARTIFACTS_DIR hoặc ./artifacts
    python scripts/check_artifacts.py --artifacts-dir D:/export
    python scripts/check_artifacts.py --skip-versions     # chưa cài torch, chỉ kiểm tra file
    python scripts/check_artifacts.py --skip-models       # model đang huấn luyện: chỉ dữ liệu demo

Mã thoát: 0 khi không có lỗi (có thể có cảnh báo), 1 khi có lỗi.
Chỉ dùng thư viện chuẩn: chạy được trước khi cài torch / torch_geometric.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path

DATASETS = ("politifact", "gossipcop")
FEATURES = ("profile", "bert")

# Khoá phiên bản trong mỗi mục của model_card.json. Notebook §10 ghi `torch` / `torch_geometric`
# ở cấp ngoài cùng của từng mục (docs/open_questions.md #2); các dạng cũ vẫn được nhận.
VERSION_KEYS = {
    "torch": (("versions", "torch"), ("torch",), ("torch_version",)),
    "torch_geometric": (
        ("versions", "torch_geometric"),
        ("versions", "pyg"),
        ("torch_geometric",),
        ("pyg",),
        ("pyg_version",),
    ),
}


@dataclass
class Report:
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def _require_file(root: Path, rel: str, report: Report) -> bool:
    if (root / rel).is_file():
        return True
    report.errors.append(f"Thiếu file: {rel}")
    return False


def _require_glob(root: Path, pattern: str, report: Report, what: str) -> list[Path]:
    found = sorted(root.glob(pattern))
    if not found:
        report.errors.append(f"Thiếu {what}: không có file khớp {pattern}")
    return found


def _lookup(card: dict, paths: tuple[tuple[str, ...], ...]) -> str | None:
    for path in paths:
        node: object = card
        for key in path:
            if not isinstance(node, dict) or key not in node:
                break
            node = node[key]
        else:
            if isinstance(node, str | int | float):
                return str(node)
    return None


def _base_version(version: str) -> str:
    """Bỏ hậu tố build (`2.3.1+cu121` → `2.3.1`), xem docs/open_questions.md #3."""
    return version.split("+", 1)[0].strip()


def check_files(
    root: Path, report: Report, models: bool = True, entries: list[dict] | None = None
) -> None:
    required = ["results.csv"]
    if models:
        required += ["models/gnn_model.py", "models/golden_predictions.json"]
    for rel in required:
        _require_file(root, rel, report)
    _require_file(root, "tables/graph_meta.csv", report)
    _require_glob(root, "tables/*.csv", report, "bảng kết quả")

    for ds in DATASETS:
        _require_file(root, f"samples/{ds}.json", report)
        for feat in FEATURES if models else ():
            _require_file(root, f"graphs/{ds}_{feat}_demo.pt", report)
            named = [
                e["file"]
                for e in entries or []
                if e.get("dataset") == ds and e.get("feature") == feat and e.get("file")
            ]
            if len(named) > 1:
                report.errors.append(f"model_card.json có nhiều model cho {ds} × {feat}.")
            if named:
                _require_file(root, f"models/{named[0]}", report)
            else:
                _require_glob(root, f"models/{ds}_{feat}_*.pt", report, f"model {ds} × {feat}")

    if not list(root.glob("figs/*.png")):
        report.warnings.append("Thư mục figs/ không có ảnh PNG; trang Results sẽ thiếu hình.")

    json_files = [f"samples/{ds}.json" for ds in DATASETS]
    if models:
        json_files.append("models/golden_predictions.json")
    for rel in json_files:
        path = root / rel
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                report.errors.append(f"{rel} không phải JSON hợp lệ: {exc}")


def load_model_card(root: Path, report: Report) -> list[dict] | None:
    """Trả danh sách mục của model card: list (mỗi mục một model) hoặc một object."""
    if not _require_file(root, "models/model_card.json", report):
        return None
    try:
        card = json.loads((root / "models/model_card.json").read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        report.errors.append(f"models/model_card.json không phải JSON hợp lệ: {exc}")
        return None
    entries = card if isinstance(card, list) else [card]
    if not entries or not all(isinstance(e, dict) for e in entries):
        report.errors.append(
            "models/model_card.json phải là một object hoặc danh sách object (mỗi model một mục)."
        )
        return None
    if any("label_map" not in e for e in entries):
        report.errors.append("models/model_card.json thiếu khoá label_map (AGENTS.md quy tắc 6).")
    elif len({json.dumps(e["label_map"], sort_keys=True) for e in entries}) > 1:
        report.errors.append("Các mục trong models/model_card.json có label_map khác nhau.")
    return entries


def installed_version(dist: str) -> str | None:
    try:
        return importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError:
        return None


def check_versions(entries: list[dict], report: Report, installed=installed_version) -> None:
    for dist, paths in VERSION_KEYS.items():
        found = {v for v in (_lookup(e, paths) for e in entries) if v is not None}
        if len(found) > 1:
            report.errors.append(f"model_card.json ghi nhiều phiên bản {dist}: {sorted(found)}.")
            continue
        expected = next(iter(found), None)
        if expected is None:
            report.warnings.append(
                f"model_card.json không ghi phiên bản {dist}; bỏ qua so phiên bản "
                "(docs/open_questions.md #2)."
            )
            continue
        actual = installed(dist)
        if actual is None:
            report.errors.append(
                f"Chưa cài {dist} (model_card.json yêu cầu {expected}). "
                "Cài đúng phiên bản hoặc chạy với --skip-versions để chỉ kiểm tra file."
            )
        elif _base_version(actual) != _base_version(expected):
            report.errors.append(
                f"Lệch phiên bản {dist}: đang cài {actual}, model_card.json yêu cầu {expected}."
            )


def check(
    root: Path, *, versions: bool = True, models: bool = True, installed=installed_version
) -> Report:
    report = Report()
    if not root.is_dir():
        report.errors.append(
            f"Không thấy thư mục artifacts: {root}. Xem scripts/fetch_artifacts.md."
        )
        return report
    if (root / "export").is_dir() and not (root / "models").is_dir():
        report.errors.append(
            "artifacts/ còn thừa một cấp export/; chuyển nội dung export/ ra ngoài."
        )
        return report
    card = load_model_card(root, report) if models else None
    check_files(root, report, models=models, entries=card)
    if models and versions and card is not None:
        check_versions(card, report, installed)
    return report


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Kiểm tra artifacts/ trước khi chạy backend.")
    default_dir = Path(__file__).resolve().parents[1] / "artifacts"
    parser.add_argument(
        "--artifacts-dir", type=Path, default=Path(os.environ.get("ARTIFACTS_DIR", default_dir))
    )
    parser.add_argument(
        "--skip-versions", action="store_true", help="không so phiên bản torch / torch_geometric"
    )
    parser.add_argument(
        "--skip-models",
        action="store_true",
        help="bỏ qua model, model card, đồ thị .pt (model đang huấn luyện)",
    )
    args = parser.parse_args(argv)

    root = args.artifacts_dir.resolve()
    report = check(root, versions=not args.skip_versions, models=not args.skip_models)
    print(f"Kiểm tra {root}")
    for msg in report.warnings:
        print(f"  CẢNH BÁO  {msg}")
    for msg in report.errors:
        print(f"  LỖI       {msg}")
    if report.ok:
        print(f"Đạt ({len(report.warnings)} cảnh báo).")
        return 0
    print(f"Không đạt: {len(report.errors)} lỗi, {len(report.warnings)} cảnh báo.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
