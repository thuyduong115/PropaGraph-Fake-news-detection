# PropaGraph – Phát hiện tin giả dựa trên đồ thị lan truyền

> Đồ án chuyên ngành 2 · Lớp 23GITB · GVHD: PGS.TS. Nguyễn Thanh Bình
> Nhóm: Trần Thị Thùy Dương · Lê Thái Lâm · Phạm Lan Nhi
> Hạn nộp: **30/11/2026**

Repo này chứa **hệ thống minh họa** cho đề tài "Phát hiện tin giả dựa trên đồ thị lan truyền bằng mạng nơ-ron đồ thị". Toàn bộ huấn luyện và thực nghiệm nằm trong notebook (`notebooks/`). Repo chỉ **suy luận** với model đã huấn luyện, trên các đồ thị test của UPFD, và trực quan hóa kết quả.

---

## 1. Phạm vi sản phẩm (đã chốt trong báo cáo tiến độ)

Hệ thống **làm**:
- Duyệt các cây lan truyền mẫu (200 đồ thị test / tập, cân bằng nhãn) của PolitiFact và GossipCop.
- Hiển thị cây lan truyền: bố cục cây/radial, màu theo thời gian, kích thước theo bậc.
- Dự đoán thật/giả kèm xác suất bằng model GNN đã huấn luyện.
- **Mô phỏng phát hiện sớm**: kéo thanh thời gian (0,5 giờ → toàn bộ), cây và xác suất cập nhật theo phần cây đã quan sát được.
- Trang kết quả thực nghiệm và trang độ tin cậy dữ liệu, đọc từ các bảng/biểu đồ notebook xuất ra.

Hệ thống **không làm**:
- Không nhận URL hay văn bản tin tức mới. UPFD không có văn bản gốc, và đặc trưng user được tính từ lịch sử tweet không còn crawl được.
- Không huấn luyện lại model trong backend.
- Không phải công cụ kiểm chứng tin tức thực tế. Giao diện phải hiển thị câu miễn trừ (xem §7).

---

## 2. Cấu trúc thư mục

```
propagraph/
├── README.md                     ← file này (kế hoạch + quy ước cho agent)
├── AGENTS.md                     ← tóm tắt quy tắc cho coding agent (tạo ở P0)
├── Makefile                      ← make setup | dev | test | lint | docker
├── docker-compose.yml
├── .env.example
├── notebooks/
│   └── DACN2_tuan3-5.ipynb       ← nguồn sự thật của mọi số liệu; chạy trên Colab
├── artifacts/                    ← KHÔNG commit (gitignore); copy từ Drive: VKU-Study/DACN2/v2/export/
│   ├── models/
│   │   ├── gnn_model.py          ← SINH TỰ ĐỘNG từ notebook, không sửa tay
│   │   ├── model_card.json       ← cấu hình, F1, phiên bản torch/pyg
│   │   ├── golden_predictions.json ← xác suất chuẩn để test parity
│   │   └── <dataset>_<feature>_<conv>.pt
│   ├── graphs/<dataset>_<feature>_demo.pt   ← list[torch_geometric.data.Data], x lưu float16
│   ├── samples/<dataset>.json    ← cùng 200 đồ thị ở dạng JSON nhẹ cho frontend
│   ├── tables/*.csv              ← E0–E6, độ tin cậy dữ liệu, graph_meta.csv
│   ├── figs/*.png
│   └── results.csv
├── backend/
│   ├── pyproject.toml            ← hoặc requirements.txt; PIN torch + torch_geometric theo model_card.json
│   ├── Dockerfile
│   ├── app/
│   │   ├── main.py               ← FastAPI app, CORS, mount routers, lifespan nạp artifacts
│   │   ├── core/config.py        ← Settings (pydantic-settings): ARTIFACTS_DIR, DEVICE, CORS_ORIGINS
│   │   ├── core/registry.py      ← nạp model_card, model .pt, graphs, samples MỘT LẦN khi khởi động
│   │   ├── services/graph_ops.py ← cut_time, to_undirected, keep_nodes (port 1:1 từ notebook)
│   │   ├── services/inference.py ← predict(dataset, feature, gid, cutoff_h) → prob
│   │   ├── services/results.py   ← đọc tables/*.csv, figs/*.png
│   │   ├── schemas/*.py          ← Pydantic models cho request/response
│   │   └── api/
│   │       ├── health.py
│   │       ├── models.py
│   │       ├── graphs.py
│   │       ├── predict.py
│   │       └── results.py
│   └── tests/
│       ├── test_parity.py        ← so với golden_predictions.json, sai số ≤ 1e-4
│       ├── test_graph_ops.py
│       └── test_api.py
├── frontend/
│   ├── package.json              ← Vite + React + TypeScript
│   ├── src/
│   │   ├── api/client.ts         ← gọi backend, kiểu dữ liệu sinh từ OpenAPI
│   │   ├── pages/
│   │   │   ├── Explorer.tsx      ← danh sách đồ thị + bộ lọc
│   │   │   ├── GraphDetail.tsx   ← cây lan truyền + thanh thời gian + dự đoán
│   │   │   ├── Results.tsx       ← bảng E0–E5 + biểu đồ
│   │   │   ├── DataReliability.tsx
│   │   │   └── About.tsx         ← phương pháp, nhóm, miễn trừ
│   │   ├── components/
│   │   │   ├── PropagationTree.tsx   ← vẽ cây (d3-hierarchy hoặc Cytoscape.js)
│   │   │   ├── TimeSlider.tsx
│   │   │   ├── PredictionGauge.tsx
│   │   │   ├── EarlyCurve.tsx        ← xác suất theo thời gian (Recharts)
│   │   │   └── ResultTable.tsx
│   │   └── styles/
│   └── Dockerfile
├── scripts/
│   ├── fetch_artifacts.md        ← hướng dẫn tải export/ từ Drive về artifacts/
│   └── check_artifacts.py        ← kiểm tra đủ file, đúng phiên bản trước khi chạy backend
└── docs/
    ├── api.md                    ← mô tả endpoint (sinh từ OpenAPI + ví dụ)
    ├── architecture.md           ← sơ đồ luồng dữ liệu notebook → artifacts → backend → frontend
    └── report/                   ← link báo cáo, slide, video demo
```

---

## 3. Luồng dữ liệu

```
Colab notebook ──(§10 xuất)──► Drive: export/ ──(copy thủ công)──► artifacts/
                                                                     │
                       backend (FastAPI) nạp 1 lần lúc khởi động ◄────┘
                                │  REST/JSON
                       frontend (React) ◄┘
```

Số liệu trên trang Kết quả **chỉ** lấy từ `artifacts/tables` và `artifacts/results.csv`. Không được gõ tay hay tự tính lại số liệu trong frontend.

---

## 4. API (FastAPI)

| Method | Path | Mô tả |
|---|---|---|
| GET | `/api/health` | trạng thái, phiên bản torch/pyg, các model đã nạp |
| GET | `/api/models` | nội dung `model_card.json` |
| GET | `/api/datasets` | `["politifact", "gossipcop"]` kèm số đồ thị demo |
| GET | `/api/datasets/{ds}/graphs` | danh sách tóm tắt: `gid, news_id, title, label, n_nodes, depth, span_h`; query: `label`, `min_nodes`, `max_nodes`, `q` (tìm theo tiêu đề), `page`, `size` |
| GET | `/api/datasets/{ds}/graphs/{gid}` | cây đầy đủ: `nodes[{id, depth, t_rel_h}]`, `edges[[src, dst]]`, metadata |
| POST | `/api/predict` | body `{dataset, gid, feature: "profile"\|"bert", cutoff_h: number\|null}` → `{prob_fake, pred_label, n_nodes_used, n_nodes_total, model}` |
| GET | `/api/datasets/{ds}/graphs/{gid}/timeline?feature=bert` | xác suất tại các mốc `[0.5, 1, 3, 6, 12, 24, 72, 168, null]` (một lần gọi cho cả thanh trượt) |
| GET | `/api/results/tables` | danh sách bảng; `/api/results/tables/{name}` trả JSON từ CSV |
| GET | `/api/results/figures/{name}` | ảnh PNG |
| POST | `/api/auth/login`, `/api/auth/logout`; GET `/api/auth/me` | đăng nhập hai vai trò `admin` / `user` ([tài khoản thử](docs/accounts.md)) |
| GET | `/api/admin/status`; POST `/api/admin/reload` | chỉ `admin`: tình trạng và nạp lại artifacts |

Chi tiết, mã lỗi và định dạng `samples/*.json`: [`docs/api.md`](docs/api.md).

Quy tắc suy luận (phải khớp notebook, xem `notebooks/…ipynb` §3):
1. Lấy `Data` từ `graphs/<ds>_<feature>_demo.pt`, đổi `x` sang float32.
2. Nếu có `cutoff_h`: giữ gốc + user có `rt <= cutoff_h`; user mất cha được **nối lại vào gốc** (`keep_nodes`).
3. Chuyển sang đồ thị vô hướng (`to_undirected`).
4. `model(batch).softmax(1)[:, 1]` = xác suất **fake**. Nhãn: `label_map` trong `model_card.json` (đã đối chiếu với FakeNewsNet trong notebook §1.1).

---

## 5. Giao diện (tuần 5 theo đề cương)

**GraphDetail**, màn hình chính của demo:
- Bên trái: cây lan truyền, nút gốc (bài báo) to và nằm giữa (bố cục radial); màu node theo `t_rel_h` (thang log); node chưa xuất hiện ở mốc thời gian hiện tại thì mờ đi.
- Bên dưới: `TimeSlider` có các mốc như API timeline. Khi kéo, cây mờ/hiện theo thời gian, đồng hồ xác suất cập nhật.
- Bên phải: `PredictionGauge` (xác suất fake, nhãn thật), `EarlyCurve` (xác suất theo thời gian), thông tin: số node, độ sâu, khoảng thời gian lan truyền, tiêu đề, link FakeNewsNet id.
- Chọn đặc trưng `profile` / `bert` bằng toggle.

**Explorer**: bảng có lọc theo nhãn và kích thước, tìm theo tiêu đề, mỗi dòng có mini-sparkline kích thước cây.

**Results**: bảng E0 (4 GNN × 4 đặc trưng + baseline), E1 (ablation cạnh), E2 (nút gốc), E3 (phát hiện sớm), E4 (GNN+), E5 (k-fold), kiểm định bootstrap E6. Mỗi bảng có 1–2 câu diễn giải **do nhóm viết** trong `frontend/src/content/results.md`. Agent chỉ để placeholder, không tự viết diễn giải.

**DataReliability**: các phát hiện ở notebook §1 (quy ước nhãn, chỉ số node ≠ thời gian, nhiễu thời gian ở PolitiFact, id GossipCop, tiêu đề trùng, nút gốc trùng user).

Yêu cầu chung: responsive, có dark mode, tiếng Việt là mặc định (chuẩn bị i18n cho tiếng Anh vì báo cáo/slide bằng tiếng Anh), không phụ thuộc CDN ngoài khi build.

---

## 6. Kế hoạch triển khai (task cho agent)

Thứ tự bắt buộc: P0 → P1 → P2 trước khi làm frontend. Mỗi task xong phải có test hoặc tiêu chí kiểm tra bên dưới.

| Pha | Task | Tiêu chí hoàn thành | Hạn |
|---|---|---|---|
| **P0** | Khung repo, `.gitignore` (bỏ `artifacts/`, `.env`), `AGENTS.md`, Makefile, pre-commit (ruff, black, eslint, prettier) | `make lint` chạy sạch | 13/11 |
| **P0** | `scripts/check_artifacts.py`: kiểm tra đủ file theo §2, so phiên bản torch/pyg với `model_card.json` | Báo lỗi rõ ràng khi thiếu file | 13/11 |
| **P1** | `core/registry.py` + `services/graph_ops.py` + `services/inference.py` | `pytest tests/test_parity.py`: mọi case trong `golden_predictions.json` sai số ≤ 1e-4 | 14/11 |
| **P1** | Router `health`, `models`, `graphs`, `predict`, `timeline` + schemas | `pytest tests/test_api.py`; `/docs` hiển thị đủ endpoint | 15/11 |
| **P2** | Router `results` (CSV → JSON, PNG) + cache | trả đúng số dòng của từng CSV | 15/11 |
| **P3** | Frontend khung: Vite + React + TS + router + layout + client sinh từ OpenAPI | `npm run build` thành công | 16/11 |
| **P3** | `PropagationTree` + `GraphDetail` với dữ liệu thật | cây 500 node render < 1 giây | 18/11 |
| **P3** | `TimeSlider` + `PredictionGauge` + `EarlyCurve` nối API timeline | kéo slider không gọi API lặp lại | 19/11 |
| **P4** | `Explorer`, `Results`, `DataReliability`, `About` | nội dung lấy 100% từ API | 21/11 |
| **P4** | Docker: `docker compose up` chạy cả hai service, artifacts mount read-only | chạy trên máy sạch theo README | 22/11 |
| **P5** | Kiểm thử thủ công theo kịch bản demo (§8), sửa lỗi, chụp ảnh màn hình cho báo cáo | checklist §8 đạt | 25/11 |
| **P5** | Quay video demo 3–5 phút, đóng băng phiên bản `v1.0.0` | tag git | 28/11 |

Song song (nhóm làm, không giao cho agent): chạy notebook trên Colab, viết báo cáo và slide, viết diễn giải kết quả.

---

## 7. Quy tắc cho coding agent

1. **Không sửa** `artifacts/**` và `artifacts/models/gnn_model.py`. Nếu cần đổi kiến trúc model thì đổi trong notebook, chạy lại §10 và copy lại artifacts.
2. **Không bịa số liệu.** Không hard-code F1, accuracy hay bất kỳ con số thực nghiệm nào trong code hoặc UI. Mọi số đi qua API từ `artifacts/`.
3. `graph_ops.py` phải port **đúng 1:1** các hàm `keep_nodes`, `cut_time`, `undirected` của notebook. Có thay đổi gì thì `test_parity.py` phải còn xanh.
4. Phiên bản `torch` và `torch_geometric` của backend phải khớp `model_card.json`. Backend chạy CPU là đủ (≤ 200 đồ thị, model nhỏ).
5. Backend nạp artifacts **một lần** trong `lifespan`, không đọc file trong mỗi request.
6. Mọi chuỗi giao diện đặt trong file i18n (`vi.json`, `en.json`), không viết cứng trong component.
7. Footer mọi trang có câu miễn trừ: *"Hệ thống minh họa cho đồ án học thuật, chỉ chạy trên dữ liệu UPFD đã công bố. Kết quả không phải là kết luận kiểm chứng thông tin."*
8. Commit nhỏ, message theo Conventional Commits (`feat(backend): …`, `fix(frontend): …`). Mỗi PR cập nhật bảng tiến độ ở §9.
9. Khi không chắc về yêu cầu, ghi câu hỏi vào `docs/open_questions.md` thay vì tự quyết định phạm vi.

---

## 8. Kịch bản demo (dùng để nghiệm thu P5)

1. Mở Explorer → lọc GossipCop, nhãn fake, 50–200 node → mở một đồ thị.
2. Kéo thanh thời gian từ 0,5 giờ đến toàn bộ: cây "lớn dần", xác suất thay đổi, đường EarlyCurve hiện đủ các mốc.
3. Đổi đặc trưng `profile` ↔ `bert`, so sánh xác suất.
4. Mở một tin thật có kích thước tương tự để so sánh hình dạng cây.
5. Mở Results → bảng E1: giải thích vì sao "star" gần với "real" (cây nông).
6. Mở DataReliability → nhiễu thời gian ở PolitiFact: lý do kết luận chính dựa trên GossipCop.

---

## 9. Tiến độ

| Hạng mục | Trạng thái |
|---|---|
| Notebook tuần 3–5 (E0–E6, xuất artifacts) | ✅ viết xong · ⏳ chạy trên Colab |
| P0 Khung repo | ✅ |
| P1 Backend suy luận + parity test | ⏳ đủ router (datasets, graphs, timeline, predict, auth, admin); suy luận chờ model đang huấn luyện và notebook (O-1) |
| P2 API kết quả | ✅ |
| P3 Trực quan hóa cây + phát hiện sớm | ⏳ cây radial, thanh thời gian, đường theo mốc xong; xác suất chờ model |
| P4 Các trang còn lại + Docker | ⏳ Explorer, Results, DataReliability, About, Hệ thống, đăng nhập xong; Docker chưa chạy thử với torch |

Cập nhật 12/11/2026. Chi tiết từng task: [`BACKLOG.md`](BACKLOG.md).
| P5 Nghiệm thu, video, v1.0.0 | ⬜ |

---

## 10. Chạy nhanh

```bash
# 0. lần đầu: .venv + thư viện backend, npm install, pre-commit
python scripts/run.py setup
# 1. dữ liệu: tải export/ từ Drive (VKU-Study/DACN2/v2/export) về ./artifacts
python scripts/check_artifacts.py --skip-models   # bỏ --skip-models khi đã có model
#    chưa có export: sinh dữ liệu GIẢ để làm giao diện, rồi đặt ARTIFACTS_DIR=.cache/dev-artifacts trong .env
python scripts/run.py devdata
# 2a. chạy dev: hai terminal
python scripts/run.py dev         # backend :8000 (/docs)
cd frontend && npm run dev        # frontend :5173
# 2b. hoặc Docker
docker compose up --build         # frontend :8080
```

Đăng nhập bằng tài khoản thử trong [`docs/accounts.md`](docs/accounts.md)
(`admin` / `admin@123`, `user` / `user@123`; chỉ dùng cho phát triển và demo).

## Nguồn dữ liệu và trích dẫn

- UPFD: Dou et al., *User Preference-aware Fake News Detection*, SIGIR 2021 · github.com/safe-graph/GNN-FakeNews
- FakeNewsNet: Shu et al., Big Data 2020 · github.com/KaiDMML/FakeNewsNet
- PyTorch Geometric: `torch_geometric.datasets.UPFD`
