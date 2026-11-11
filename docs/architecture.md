# Kiến trúc

## Luồng dữ liệu

```text
┌──────────────────────┐  §10 xuất   ┌────────────────────┐  copy tay  ┌──────────────┐
│ Colab notebook       │ ──────────► │ Drive: export/     │ ─────────► │ artifacts/   │
│ DACN2_v2.ipynb       │             │ VKU-Study/DACN2/v2 │            │ (read-only)  │
└──────────────────────┘             └────────────────────┘            └──────┬───────┘
                                                                              │ nạp 1 lần
                                                                              ▼ (lifespan)
┌──────────────────────┐   /api/*    ┌─────────────────────────────────────────────────┐
│ frontend (React)     │ ◄────────── │ backend (FastAPI)                               │
│ Vite + TS, i18n vi/en│  REST/JSON  │ core/registry → services/{graph_ops, inference, │
└──────────────────────┘             │ results} → api/{health, models, graphs, ...}    │
                                     └─────────────────────────────────────────────────┘
```

## Thành phần

| Thành phần | Công nghệ | Ghi chú |
| --- | --- | --- |
| Notebook | Colab, PyTorch Geometric | Nguồn sự thật của số liệu; không chạy trong repo |
| `scripts/check_artifacts.py` | Python stdlib | Chạy trước backend; không cần torch để kiểm tra file |
| Backend | FastAPI, pydantic-settings, torch + torch_geometric (CPU) | Không DB, không hàng đợi; trạng thái chỉ là artifacts đã nạp trong RAM |
| Frontend | Vite + React + TypeScript | Client sinh từ OpenAPI; không CDN ngoài khi build |
| Docker (P4) | `docker compose` 2 service | `artifacts/` mount read-only |

## Vì sao không có…

- **Cơ sở dữ liệu**: ≤ 200 đồ thị / tập, chỉ đọc, nạp vào RAM dư sức. Thêm DB tạo thêm nguồn
  sự thật thứ hai cho số liệu.
- **GPU**: model nhỏ, suy luận từng đồ thị; CPU đủ nhanh cho demo.
- **Huấn luyện trong backend**: ngoài phạm vi (docs/development.md §1); mọi thay đổi model đi qua notebook.

## Cấu trúc thư mục

Xem docs/development.md §2. Hiện trạng 12/11/2026:

```text
backend/app/
  main.py                 FastAPI, CORS, lifespan nạp Registry
  core/config.py          Settings (ARTIFACTS_DIR tính từ gốc repo, AUTH_*)
  core/registry.py        nạp model card, samples, bảng, hình MỘT LẦN; model .pt: P1-1
  core/auth.py            hai tài khoản cấu hình, cookie phiên ký HMAC (docs/accounts.md)
  services/samples.py     đọc samples/*.json, tóm tắt cây, đếm node theo mốc
  services/results.py     đọc tables/*.csv, results.csv, figs/*.png (giữ nguyên chuỗi)
  services/inference.py   chưa có model: báo 503 rõ ràng (P1-1)
  api/                    health, auth, models, graphs (datasets, timeline), predict,
                          results, admin
backend/tests/            41 test: API, auth, graphs, results, check_artifacts
frontend/src/
  api/                    client (cookie cùng origin), useApi (cache theo URL), types
  auth/                   AuthProvider, RequireAuth, RequireAdmin
  components/             PropagationTree, TimeSlider, PredictionGauge, EarlyCurve,
                          TimeLegend, Sparkline, ResultTable, Segmented, StateView, Layout
  pages/                  Login, Explorer, GraphDetail, Results, DataReliability, About,
                          Admin, NotFound
  lib/                    tree (bố cục radial d3-hierarchy), timeScale, format, markdown
  content/                results.md, data_reliability.md (nhóm viết)
  i18n/                   vi.json (mặc định), en.json
scripts/                  check_artifacts.py, make_dev_artifacts.py, run.py
```

## Giao diện

- Đọc dữ liệu (Operate): trung tính, màu dành cho dữ liệu. Token màu sáng/tối ở
  `styles/global.css`; thang thời gian 5 bậc `--t0…--t4` có bộ riêng cho chế độ tối.
- Cây radial: gốc (bản tin) ở giữa, mỗi vòng một mức độ sâu, con xếp theo thời gian; kéo thanh
  thời gian chỉ đổi class mờ/hiện, không tính lại bố cục.
- Timeline lấy một lần cho mỗi đặc trưng; `useApi` cache theo URL nên kéo thanh trượt hay quay
  lại trang không gọi API lặp lại.
- Font Be Vietnam Pro tự host (@fontsource), icon lucide-react; không CDN khi build.
- Kiểm tra trên Edge (Playwright, 12/11): không lỗi JS, không cuộn ngang ở 375 px, cây 384
  node hiện trong ~0,5 giây (dữ liệu giả).
