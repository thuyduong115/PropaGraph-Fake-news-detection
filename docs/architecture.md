# Kiến trúc

## Luồng dữ liệu

```text
┌──────────────────────┐  §10 xuất   ┌────────────────────┐  copy tay  ┌──────────────┐
│ Colab notebook       │ ──────────► │ Drive: export/     │ ─────────► │ artifacts/   │
│ DACN2_tuan3-5.ipynb  │             │ VKU-Study/DACN2/v2 │            │ (read-only)  │
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
- **Huấn luyện trong backend**: ngoài phạm vi (README §1); mọi thay đổi model đi qua notebook.

## Cấu trúc thư mục

Xem README §2. Phần đã có ở P0:

```text
backend/app/{main.py, core/config.py, core/registry.py, api/health.py, api/models.py, schemas/}
backend/tests/{test_api.py, test_check_artifacts.py}
backend/Dockerfile, frontend/Dockerfile (nginx, proxy /api), docker-compose.yml
frontend/src/{App.tsx, components/Layout.tsx, pages/*, i18n/{vi,en}.json, api/client.ts}
scripts/{check_artifacts.py, run.py, fetch_artifacts.md}
```
