# Product Backlog

Hạn nộp: **30/11/2026**. Trạng thái: To Do / In Progress / Done.

**Cập nhật file này ngay khi xong một việc**, trong cùng commit/PR, kèm bảng tiến độ README §9
(`AGENTS.md` quy tắc 15).

Đối chiếu đề cương (DCCT_DACN2): tuần 4 (03–09/11) backend suy luận FastAPI; tuần 5 (10–16/11)
giao diện trực quan hóa cây; tuần 6 (17–23/11) tích hợp và kiểm thử; tuần 7 (24–30/11) báo cáo,
slide tiếng Anh. Phần huấn luyện model do nhóm chạy trên Colab, không thuộc backlog này.

## Hệ thống minh họa (README §6)

| ID | Task | Tiêu chí hoàn thành | Hạn | Trạng thái |
|---|---|---|---|---|
| P0-1 | Khung repo, `.gitignore`, `AGENTS.md`, `DATA_BOUNDARY.md`, Makefile + `scripts/run.py`, pre-commit (ruff, black, eslint, prettier), CI | `make lint` / `python scripts/run.py lint` sạch | 13/11 | Done |
| P0-2 | `scripts/check_artifacts.py`: đủ file theo §2, so phiên bản torch/pyg với `model_card.json`; `--skip-models` khi model đang huấn luyện | Báo lỗi rõ khi thiếu file; test với artifacts giả | 13/11 | Done |
| P1-1 | `core/registry.py` + `services/graph_ops.py` + `services/inference.py`. Đã có: registry nạp model card, samples, bảng, hình; `inference.py` trả 503 rõ ràng khi chưa có model. Còn: nạp model `.pt` và đồ thị `.pt`, port 1:1 `graph_ops`, `test_parity.py` (chờ model đang huấn luyện và O-1) | `pytest tests/test_parity.py` sai số ≤ 1e-4 | 14/11 | In Progress |
| P1-2 | Router `health`, `models`, `graphs`, `predict`, `timeline` + schemas. Đã có đủ router; `timeline` trả số node mọi mốc, `prob_fake = null` tới khi có model; `predict` trả 503 tới khi có model | `pytest tests/test_api.py`; `/docs` đủ endpoint | 15/11 | In Progress |
| P2-1 | Router `results` (CSV → JSON, PNG), nạp một lần khi khởi động, nhóm bảng theo tên | Trả đúng số dòng từng CSV (`tests/test_results.py`) | 15/11 | Done |
| P3-1 | Frontend khung: Vite + React + TS + router + layout + i18n vi/en + dark mode + đăng nhập. Kiểu dữ liệu viết tay ở `api/types.ts`; sinh `schema.d.ts` bằng `npm run gen:api` khi API chốt | `npm run build` thành công | 16/11 | Done |
| P3-2 | `PropagationTree` (radial, màu theo thời gian thang log, kích thước theo số lượt chia sẻ tiếp) + `GraphDetail`. Đã đo trên dữ liệu giả: cây 384 node hiện trong ~0,5 giây kể cả tải API. Còn đo lại với dữ liệu thật | Cây 500 node render < 1 giây | 18/11 | In Progress |
| P3-3 | `TimeSlider` + `PredictionGauge` + `EarlyCurve` nối API timeline. Kéo qua 9 mốc: 0 lần gọi API. Gauge và đường xác suất hiện trạng thái "chưa có dự đoán" tới khi có model | Kéo slider không gọi API lặp lại | 19/11 | In Progress |
| P4-1 | `Explorer` (lọc nhãn, số node, tìm tiêu đề, sắp xếp, phân trang, sparkline), `Results`, `DataReliability`, `About`, trang `Hệ thống` cho admin | Nội dung lấy 100% từ API | 21/11 | Done |
| P4-2 | Docker: `docker compose up` chạy cả hai service, artifacts mount read-only (đã có Dockerfile + compose; chưa chạy thử với torch thật) | Chạy trên máy sạch theo README | 22/11 | In Progress |
| P5-1 | Kiểm thử thủ công theo kịch bản demo (§8), sửa lỗi, chụp ảnh màn hình (chỉ với dữ liệu thật) | Checklist §8 đạt | 25/11 | To Do |
| P5-2 | Video demo 3–5 phút, đóng băng `v1.0.0` | Tag git | 28/11 | To Do |

## Việc phát sinh

| ID | Task | Trạng thái |
|---|---|---|
| O-1 | Đưa `notebooks/DACN2_tuan3-5.ipynb` vào repo (đang chặn port 1:1 `graph_ops` ở P1-1) | To Do |
| O-2 | Thêm hook eslint + prettier vào `.pre-commit-config.yaml` và job frontend vào CI | Done |
| O-3 | Chốt các câu hỏi trong `docs/open_questions.md` | To Do |
| O-4 | Đăng nhập hai vai trò `admin` / `user`, tài khoản thử ghi ở `docs/accounts.md`; `AUTH_REQUIRED=0` để tắt | Done |
| O-5 | `scripts/make_dev_artifacts.py`: artifacts GIẢ để làm giao diện khi chưa có export; giao diện hiện cảnh báo dữ liệu giả | Done |
| O-6 | Notebook §10 xuất `samples/<dataset>.json` theo định dạng ở `docs/api.md` | To Do |
| O-7 | Nhóm viết diễn giải trong `frontend/src/content/results.md` và `data_reliability.md` | To Do |
| O-8 | CI GitHub Actions báo `startup_failure` (cả repo cũ): kiểm tra Billing/Actions của tài khoản | To Do |

## Việc cần làm tiếp theo

- [x] P0-1 khung repo
- [x] P0-2 `check_artifacts.py`
- [x] P2-1 API kết quả
- [x] P3-1 khung frontend, P4-1 các trang
- [ ] O-6 notebook xuất `samples/*.json`; copy `export/` về `artifacts/`, chạy
      `python scripts/check_artifacts.py --skip-models`
- [ ] O-1 đưa notebook vào repo
- [ ] P1-1 khi model huấn luyện xong: nạp model, port `graph_ops`, parity test, mở `predict`
- [ ] P3-2 đo lại tốc độ vẽ với dữ liệu thật
