# Product Backlog

Hạn nộp: **30/11/2026**. Trạng thái: To Do / In Progress / Done.

**Cập nhật file này ngay khi xong một việc**, trong cùng commit/PR, kèm bảng tiến độ README §9
(`AGENTS.md` quy tắc 13).

## Hệ thống minh họa (README §6)

| ID | Task | Tiêu chí hoàn thành | Hạn | Trạng thái |
|---|---|---|---|---|
| P0-1 | Khung repo, `.gitignore`, `AGENTS.md`, `DATA_BOUNDARY.md`, Makefile + `scripts/run.py`, pre-commit (ruff, black, eslint, prettier), CI | `make lint` / `python scripts/run.py lint` sạch | 13/11 | Done |
| P0-2 | `scripts/check_artifacts.py`: đủ file theo §2, so phiên bản torch/pyg với `model_card.json` | Báo lỗi rõ khi thiếu file; test với artifacts giả | 13/11 | Done |
| P1-1 | `core/registry.py` (nạp model, graphs, samples) + `services/graph_ops.py` + `services/inference.py` (registry đã nạp `model_card.json`; còn lại chờ O-1) | `pytest tests/test_parity.py` sai số ≤ 1e-4 | 14/11 | In Progress |
| P1-2 | Router `health`, `models`, `graphs`, `predict`, `timeline` + schemas (đã có `health`, `models`) | `pytest tests/test_api.py`; `/docs` đủ endpoint | 15/11 | In Progress |
| P2-1 | Router `results` (CSV → JSON, PNG) + cache | Trả đúng số dòng từng CSV | 15/11 | To Do |
| P3-1 | Frontend khung: Vite + React + TS + router + layout + i18n + client sinh từ OpenAPI (đã có khung, route, i18n vi/en, dark mode, footer miễn trừ; còn sinh `schema.d.ts` khi đủ endpoint P1-2) | `npm run build` thành công | 16/11 | In Progress |
| P3-2 | `PropagationTree` + `GraphDetail` với dữ liệu thật | Cây 500 node render < 1 giây | 18/11 | To Do |
| P3-3 | `TimeSlider` + `PredictionGauge` + `EarlyCurve` nối API timeline | Kéo slider không gọi API lặp lại | 19/11 | To Do |
| P4-1 | `Explorer`, `Results`, `DataReliability`, `About` | Nội dung lấy 100% từ API | 21/11 | To Do |
| P4-2 | Docker: `docker compose up` chạy cả hai service, artifacts mount read-only (đã có Dockerfile + compose; chưa chạy thử với torch thật) | Chạy trên máy sạch theo README | 22/11 | In Progress |
| P5-1 | Kiểm thử thủ công theo kịch bản demo (§8), sửa lỗi, chụp ảnh màn hình | Checklist §8 đạt | 25/11 | To Do |
| P5-2 | Video demo 3–5 phút, đóng băng `v1.0.0` | Tag git | 28/11 | To Do |

## Việc phát sinh

| ID | Task | Trạng thái |
|---|---|---|
| O-1 | Đưa `notebooks/DACN2_tuan3-5.ipynb` vào repo (đang chặn port 1:1 `graph_ops` ở P1-1) | To Do |
| O-2 | Thêm hook eslint + prettier vào `.pre-commit-config.yaml` và job frontend vào CI khi có `frontend/` (P3-1) | Done |
| O-3 | Chốt các câu hỏi trong `docs/open_questions.md` (khoá phiên bản trong model card, chọn `<conv>`) | To Do |

## Việc cần làm tiếp theo

- [x] P0-1 khung repo
- [x] P0-2 `check_artifacts.py`
- [ ] O-1 đưa notebook vào repo
- [ ] Copy `export/` từ Drive về `artifacts/`, chạy `python scripts/check_artifacts.py`
- [ ] P1-1 `graph_ops` + inference + parity test
