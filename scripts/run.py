"""Chạy các lệnh phát triển trên mọi hệ điều hành (thay cho Makefile trên Windows).

python scripts/run.py setup    # tạo .venv, cài backend + công cụ dev, cài pre-commit hook
python scripts/run.py lint     # ruff check + black --check
python scripts/run.py format   # ruff --fix + black
python scripts/run.py test     # pytest backend
python scripts/run.py dev      # uvicorn --reload trên :8000
python scripts/run.py check    # scripts/check_artifacts.py
python scripts/run.py web      # typecheck + build frontend
(frontend dev: cd frontend && npm run dev  → :5173)
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VENV = ROOT / ".venv"
BIN = VENV / ("Scripts" if os.name == "nt" else "bin")
LINT_PATHS = ["backend", "scripts"]
WEB = ROOT / "frontend"


def _py() -> str:
    """Python của .venv nếu đã có, nếu không thì Python đang chạy script."""
    exe = BIN / ("python.exe" if os.name == "nt" else "python")
    return str(exe) if exe.exists() else sys.executable


def _run(*args: str, cwd: Path = ROOT) -> None:
    print("$", " ".join(args), flush=True)
    code = subprocess.call(list(args), cwd=cwd)
    if code:
        sys.exit(code)


def _npm(*args: str) -> None:
    npm = shutil.which("npm")  # Windows: npm.cmd
    if npm is None:
        sys.exit("Không tìm thấy npm; cài Node.js 22 để làm frontend.")
    _run(npm, *args, cwd=WEB)


def setup() -> None:
    if not VENV.exists():
        print(f"Tạo môi trường ảo {VENV}")
        venv.create(VENV, with_pip=True)
    _run(_py(), "-m", "pip", "install", "--upgrade", "pip")
    _run(_py(), "-m", "pip", "install", "-e", "backend[dev]")
    _run(_py(), "-m", "pre_commit", "install")
    _npm("install", "--no-audit", "--no-fund")
    print("Xong. torch + torch_geometric cài riêng theo model_card.json (xem README).")


def lint() -> None:
    _run(_py(), "-m", "ruff", "check", *LINT_PATHS)
    _run(_py(), "-m", "black", "--check", *LINT_PATHS)
    _npm("run", "lint")
    _npm("run", "format:check")


def fmt() -> None:
    _run(_py(), "-m", "ruff", "check", "--fix", *LINT_PATHS)
    _run(_py(), "-m", "black", *LINT_PATHS)
    _npm("run", "format")


def test() -> None:
    _run(_py(), "-m", "pytest", "-q", cwd=ROOT / "backend")


def dev() -> None:
    _run(
        _py(),
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--port",
        "8000",
        cwd=ROOT / "backend",
    )


def web() -> None:
    _npm("run", "build")


def check() -> None:
    _run(_py(), str(ROOT / "scripts" / "check_artifacts.py"), *sys.argv[2:])


COMMANDS = {
    "setup": setup,
    "lint": lint,
    "format": fmt,
    "test": test,
    "dev": dev,
    "check": check,
    "web": web,
}

if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")  # console Windows mặc định cp1252
    if len(sys.argv) < 2 or sys.argv[1] not in COMMANDS:
        print(__doc__)
        sys.exit(2)
    COMMANDS[sys.argv[1]]()
