# Product Backlog

Hạn nộp: **30/11/2026**. Trạng thái: To Do / In Progress / Done.

**Cập nhật file này ngay khi xong một việc**, trong cùng commit/PR, kèm bảng tiến độ docs/development.md §9
(`AGENTS.md` quy tắc 15).

Đối chiếu đề cương (DCCT_DACN2): tuần 4 (03–09/11) backend suy luận FastAPI; tuần 5 (10–16/11)
giao diện trực quan hóa cây; tuần 6 (17–23/11) tích hợp và kiểm thử; tuần 7 (24–30/11) báo cáo,
slide tiếng Anh. Phần huấn luyện model do nhóm chạy trên Colab, không thuộc backlog này.

## Hệ thống minh họa (docs/development.md §6)

| ID | Task | Tiêu chí hoàn thành | Hạn | Trạng thái |
|---|---|---|---|---|
| P0-1 | Khung repo, `.gitignore`, `AGENTS.md`, `DATA_BOUNDARY.md`, Makefile + `scripts/run.py`, pre-commit (ruff, black, eslint, prettier), CI | `make lint` / `python scripts/run.py lint` sạch | 13/11 | Done |
| P0-2 | `scripts/check_artifacts.py`: đủ file theo §2, so phiên bản torch/pyg với `model_card.json`; `--skip-models` khi model đang huấn luyện | Báo lỗi rõ khi thiếu file; test với artifacts giả | 13/11 | Done |
| P1-1 | `core/registry.py` + `services/graph_ops.py` + `services/inference.py`: nạp model card (danh sách 4 model), model `.pt`, đồ thị `.pt` một lần; `graph_ops` port 1:1 notebook §3; `test_parity.py` so 240 ca golden | `pytest tests/test_parity.py` sai số ≤ 1e-4 | 14/11 | Done |
| P1-2 | Router `health`, `models`, `graphs`, `predict`, `timeline` + schemas. `timeline` trả số node và `prob_fake` mọi mốc (một lần forward); `predict` trả 503 khi chưa nạp model | `pytest tests/test_api.py`; `/docs` đủ endpoint | 15/11 | Done |
| P2-1 | Router `results` (CSV → JSON, PNG), nạp một lần khi khởi động, nhóm bảng theo tên | Trả đúng số dòng từng CSV (`tests/test_results.py`) | 15/11 | Done |
| P3-1 | Frontend khung: Vite + React + TS + router + layout + i18n vi/en + dark mode + đăng nhập. Kiểu dữ liệu viết tay ở `api/types.ts`; sinh `schema.d.ts` bằng `npm run gen:api` khi API chốt | `npm run build` thành công | 16/11 | Done |
| P3-2 | `PropagationTree` (radial, màu theo thời gian thang log, kích thước theo số lượt chia sẻ tiếp) + `GraphDetail`. Đã đo trên dữ liệu giả: cây 384 node hiện trong ~0,5 giây kể cả tải API. Dữ liệu thật: cây 497 node vẽ đúng, API chi tiết + timeline 112 ms; còn đo thời gian vẽ trong trình duyệt | Cây 500 node render < 1 giây | 18/11 | In Progress |
| P3-3 | `TimeSlider` + `PredictionGauge` + `EarlyCurve` nối API timeline. Kéo qua 9 mốc: 0 lần gọi API. Gauge và đường xác suất hiện trạng thái "chưa có dự đoán" tới khi có model | Kéo slider không gọi API lặp lại | 19/11 | In Progress |
| P4-1 | `Explorer` (lọc nhãn, số node, tìm tiêu đề, sắp xếp, phân trang, sparkline), `Results`, `DataReliability`, `About`, trang `Hệ thống` cho admin | Nội dung lấy 100% từ API | 21/11 | Done |
| P4-2 | Docker: `docker compose up` chạy cả hai service, artifacts mount read-only (đã có Dockerfile + compose; chưa chạy thử với torch thật) | Chạy trên máy sạch theo README | 22/11 | In Progress |
| P5-1 | Kiểm thử thủ công theo kịch bản demo (§8), sửa lỗi, chụp ảnh màn hình (chỉ với dữ liệu thật) | Checklist §8 đạt | 25/11 | To Do |
| P5-2 | Video demo 3–5 phút, đóng băng `v1.0.0` | Tag git | 28/11 | To Do |

## Việc phát sinh

| ID | Task | Trạng thái |
|---|---|---|
| O-1 | Notebook vào repo: quyết định 12/11 **không commit**; `notebooks/*.ipynb` chỉ giữ trên máy (`.gitignore`), `graph_ops.py` ghi rõ ô nguồn | Done |
| O-2 | Thêm hook eslint + prettier vào `.pre-commit-config.yaml` và job frontend vào CI | Done |
| O-3 | Chốt các câu hỏi trong `docs/open_questions.md` | To Do |
| O-4 | Đăng nhập hai vai trò `admin` / `user`, tài khoản thử ghi ở `docs/accounts.md`; `AUTH_REQUIRED=0` để tắt | Done |
| O-5 | `scripts/make_dev_artifacts.py`: artifacts GIẢ để làm giao diện khi chưa có export; giao diện hiện cảnh báo dữ liệu giả | Done |
| O-6 | Notebook §10 xuất `samples/<dataset>.json` theo định dạng ở `docs/api.md` | Done |
| O-7 | Nhóm viết diễn giải trong `frontend/src/content/results.md` và `data_reliability.md` | To Do |
| O-8 | CI GitHub Actions báo `startup_failure` (cả repo cũ): kiểm tra Billing/Actions của tài khoản | To Do |
| O-9 | `model_card.json` thật là danh sách (mỗi model một mục): `check_artifacts.py` và registry nhận dạng này; ghim `torch==2.14.1`, `torch_geometric==2.8.1` (bản CPU) trong `backend[ml]` | Done |
| O-10 | Sửa sau khi kiểm tra với dữ liệu thật: bảng `ALL_*` lên trang Kết quả; chú thích thang màu ghi rõ là thang chung; bán kính vòng cây theo số node + so le (cây 497 node không còn dồn); bảng pivot nhiều tầng tiêu đề (E0) hiển thị đúng | Done |

## Việc cần làm tiếp theo

- [x] P0-1 khung repo
- [x] P0-2 `check_artifacts.py`
- [x] P2-1 API kết quả
- [x] P3-1 khung frontend, P4-1 các trang
- [x] O-6 notebook xuất `samples/*.json`; đã copy `export/` về `artifacts/`
- [x] P1-1 nạp model, port `graph_ops`, parity test, mở `predict`
- [ ] P3-2, P3-3 kiểm tra giao diện (cây, gauge, đường xác suất) với dữ liệu thật
- [ ] P4-2 chạy thử Docker với torch CPU
