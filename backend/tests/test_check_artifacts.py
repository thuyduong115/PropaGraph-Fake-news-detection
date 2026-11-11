"""Test cho scripts/check_artifacts.py (BACKLOG P0-2)."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

from tests.conftest import make_fake_artifacts

_SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "check_artifacts.py"
_spec = importlib.util.spec_from_file_location("check_artifacts", _SCRIPT)
ca = importlib.util.module_from_spec(_spec)
sys.modules["check_artifacts"] = ca
_spec.loader.exec_module(ca)


def _installed(versions: dict[str, str]):
    return lambda dist: versions.get(dist)


def test_complete_tree_passes_without_version_check(fake_artifacts: Path) -> None:
    report = ca.check(fake_artifacts, versions=False)
    assert report.ok, report.errors


def test_missing_dir_is_error(tmp_path: Path) -> None:
    report = ca.check(tmp_path / "khong-co")
    assert not report.ok


def test_missing_files_are_listed(fake_artifacts: Path) -> None:
    (fake_artifacts / "graphs/gossipcop_bert_demo.pt").unlink()
    (fake_artifacts / "models/politifact_profile_fakeconv.pt").unlink()
    report = ca.check(fake_artifacts, versions=False)
    joined = "\n".join(report.errors)
    assert "graphs/gossipcop_bert_demo.pt" in joined
    assert "politifact_profile_*.pt" in joined


def test_nested_export_dir_is_reported(tmp_path: Path) -> None:
    make_fake_artifacts(tmp_path / "artifacts" / "export")
    report = ca.check(tmp_path / "artifacts")
    assert any("export/" in e for e in report.errors)


def test_label_map_required(tmp_path: Path) -> None:
    root = make_fake_artifacts(tmp_path / "a", card={"versions": {}})
    report = ca.check(root, versions=False)
    assert any("label_map" in e for e in report.errors)


def test_invalid_json_is_error(fake_artifacts: Path) -> None:
    (fake_artifacts / "samples/politifact.json").write_text("{khong hop le", encoding="utf-8")
    report = ca.check(fake_artifacts, versions=False)
    assert any("samples/politifact.json" in e for e in report.errors)


def test_version_match_ignores_build_suffix(tmp_path: Path) -> None:
    card = {"label_map": {}, "versions": {"torch": "2.3.1+cu121", "torch_geometric": "2.5.3"}}
    root = make_fake_artifacts(tmp_path / "a", card=card)
    installed = _installed({"torch": "2.3.1+cpu", "torch_geometric": "2.5.3"})
    report = ca.check(root, installed=installed)
    assert report.ok, report.errors


def test_version_mismatch_is_error(tmp_path: Path) -> None:
    card = {"label_map": {}, "torch": "2.3.1", "pyg": "2.5.3"}
    root = make_fake_artifacts(tmp_path / "a", card=card)
    installed = _installed({"torch": "2.4.0", "torch_geometric": "2.5.3"})
    report = ca.check(root, installed=installed)
    assert any("Lệch phiên bản torch" in e for e in report.errors)
    assert not any("torch_geometric" in e for e in report.errors)


def test_torch_not_installed_is_error(tmp_path: Path) -> None:
    card = {"label_map": {}, "versions": {"torch": "2.3.1", "torch_geometric": "2.5.3"}}
    root = make_fake_artifacts(tmp_path / "a", card=card)
    report = ca.check(root, installed=_installed({}))
    assert any("Chưa cài torch" in e for e in report.errors)


def test_missing_version_keys_only_warn(fake_artifacts: Path) -> None:
    report = ca.check(fake_artifacts, installed=_installed({}))
    assert report.ok
    assert len(report.warnings) == 2


def test_main_exit_codes(fake_artifacts: Path, tmp_path: Path) -> None:
    assert ca.main(["--artifacts-dir", str(fake_artifacts), "--skip-versions"]) == 0
    assert ca.main(["--artifacts-dir", str(tmp_path / "khong-co")]) == 1


def test_skip_models_only_checks_demo_data(tmp_path: Path) -> None:
    root = make_fake_artifacts(tmp_path / "a")
    for p in (root / "models").iterdir():
        p.unlink()
    for p in (root / "graphs").iterdir():
        p.unlink()
    assert not ca.check(root, versions=False).ok
    assert ca.check(root, models=False).ok


def _list_card(**extra) -> list[dict]:
    """Model card dạng danh sách như notebook §10 xuất (giá trị giả)."""
    return [
        {"dataset": ds, "feature": f, "file": f"{ds}_{f}_fakeconv.pt", "label_map": {}, **extra}
        for ds in ("politifact", "gossipcop")
        for f in ("profile", "bert")
    ]


def test_list_card_passes(tmp_path: Path) -> None:
    card = _list_card(torch="2.3.1+cu121", torch_geometric="2.5.3")
    root = make_fake_artifacts(tmp_path / "a", card=card)
    installed = _installed({"torch": "2.3.1+cpu", "torch_geometric": "2.5.3"})
    report = ca.check(root, installed=installed)
    assert report.ok, report.errors


def test_list_card_named_file_must_exist(tmp_path: Path) -> None:
    card = _list_card()
    card[0]["file"] = "khong_co.pt"
    root = make_fake_artifacts(tmp_path / "a", card=card)
    report = ca.check(root, versions=False)
    assert any("models/khong_co.pt" in e for e in report.errors)


def test_list_card_label_maps_must_agree(tmp_path: Path) -> None:
    card = _list_card()
    card[1]["label_map"] = {"0": "x"}
    root = make_fake_artifacts(tmp_path / "a", card=card)
    assert any("label_map khác nhau" in e for e in ca.check(root, versions=False).errors)
