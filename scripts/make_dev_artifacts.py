"""Sinh artifacts GIẢ để phát triển giao diện khi chưa có bản export thật.

    python scripts/make_dev_artifacts.py            # ghi vào .cache/dev-artifacts
    # rồi đặt ARTIFACTS_DIR=.cache/dev-artifacts trong .env

Mọi file đều đánh dấu giả: samples có `"synthetic": true` (giao diện hiện cảnh báo), bảng có
cột `ghi_chu = du lieu gia`. Không có model_card và model: đúng tình trạng model đang huấn
luyện. KHÔNG dùng số liệu ở đây trong báo cáo, slide hay ảnh chụp màn hình (AGENTS.md quy tắc 2).
"""

from __future__ import annotations

import argparse
import csv
import json
import random
import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATASETS = ("politifact", "gossipcop")
NOTE = "du lieu gia"


def make_tree(rng: random.Random, gid: int, label: str) -> dict:
    n = int(rng.lognormvariate(3.5, 1.0)) + 2
    n = min(n, 600)
    nodes = [{"id": 0, "depth": 0, "t_rel_h": 0.0}]
    edges = []
    for i in range(1, n):
        # cây nông kiểu "sao" xen cây sâu: chỉ để thử bố cục, không mô phỏng thống kê thật
        parent = 0 if rng.random() < 0.6 else rng.randrange(0, i)
        depth = nodes[parent]["depth"] + 1
        t = round(nodes[parent]["t_rel_h"] + rng.expovariate(1 / 8.0), 3)
        nodes.append({"id": i, "depth": depth, "t_rel_h": t})
        edges.append([parent, i])
    return {
        "gid": gid,
        "news_id": f"synthetic-{gid:04d}",
        "title": f"Bản tin giả lập số {gid} ({label})",
        "label": label,
        "nodes": nodes,
        "edges": edges,
    }


def tiny_png(path: Path, rgb: tuple[int, int, int]) -> None:
    w = h = 8
    raw = b"".join(b"\x00" + bytes(rgb) * w for _ in range(h))

    def chunk(kind: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + kind
            + data
            + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw))
        + chunk(b"IEND", b"")
    )


def write_csv(path: Path, columns: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(columns)
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", type=Path, default=ROOT / ".cache" / "dev-artifacts")
    parser.add_argument("--per-dataset", type=int, default=40)
    parser.add_argument("--seed", type=int, default=0)
    args = parser.parse_args(argv)

    rng = random.Random(args.seed)
    out: Path = args.out
    for sub in ("samples", "tables", "figs"):
        (out / sub).mkdir(parents=True, exist_ok=True)

    for ds in DATASETS:
        graphs = [
            make_tree(rng, gid, "fake" if gid % 2 else "real") for gid in range(args.per_dataset)
        ]
        payload = {"synthetic": True, "dataset": ds, "graphs": graphs}
        (out / "samples" / f"{ds}.json").write_text(json.dumps(payload), encoding="utf-8")

    def r() -> str:
        return f"{rng.random():.3f}"

    cols = ["model", "feature", "dataset", "metric_a", "metric_b", "ghi_chu"]
    rows = [
        [m, f, d, r(), r(), NOTE]
        for m in ("GCN", "GAT", "SAGE", "GIN")
        for f in ("profile", "bert")
        for d in DATASETS
    ]
    write_csv(out / "tables" / "E0_synthetic.csv", cols, rows)
    write_csv(
        out / "tables" / "E3_synthetic.csv",
        ["cutoff_h", "dataset", "metric_a", "ghi_chu"],
        [[str(c), d, r(), NOTE] for c in (0.5, 1, 3, 6, 12, 24) for d in DATASETS],
    )
    write_csv(
        out / "tables" / "R1_synthetic.csv",
        ["finding", "dataset", "count", "ghi_chu"],
        [["vi du phat hien", d, str(rng.randint(1, 50)), NOTE] for d in DATASETS],
    )
    write_csv(out / "tables" / "graph_meta.csv", ["gid", "ghi_chu"], [["0", NOTE]])
    write_csv(out / "results.csv", ["model", "metric_a", "ghi_chu"], [["GCN", r(), NOTE]])
    tiny_png(out / "figs" / "synthetic_figure.png", (90, 120, 200))

    print(f"Đã sinh artifacts GIẢ tại {out}")
    print("Đặt ARTIFACTS_DIR=.cache/dev-artifacts trong .env để backend dùng.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
