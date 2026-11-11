# Hướng dẫn cho người đóng góp và AI agent

Repo này là **PropaGraph**: hệ thống minh họa cho đồ án chuyên ngành 2 "Phát hiện tin giả dựa
trên đồ thị lan truyền bằng mạng nơ-ron đồ thị". Hệ thống chỉ **suy luận** với model đã huấn
luyện trong notebook, trên đồ thị test của UPFD, và trực quan hóa kết quả. Mọi thay đổi phải
đúng ở hai mặt: **chạy được khi demo**, và **trung thực khi đưa vào báo cáo**.

Đọc trước khi sửa:

| File | Khi nào cần |
| --- | --- |
| [`README.md`](README.md) | Phạm vi, API, giao diện, kế hoạch P0–P5, kịch bản demo |
| [`DATA_BOUNDARY.md`](DATA_BOUNDARY.md) | Mọi thay đổi chạm tới artifacts, số liệu, endpoint, trang giao diện |
| [`docs/architecture.md`](docs/architecture.md) | Thêm thành phần mới, đổi luồng dữ liệu |
| [`docs/open_questions.md`](docs/open_questions.md) | Trước khi tự quyết một điểm chưa rõ trong yêu cầu |
| [`CONTRIBUTING.md`](CONTRIBUTING.md) | Nhánh, commit, PR |
| [`BACKLOG.md`](BACKLOG.md) | Task đang làm và mã task (`P1-1`, `O-2`…) |

## Các tầng của hệ thống

| Tầng | Mã nguồn | Việc của tầng | Không làm |
| --- | --- | --- | --- |
| Thực nghiệm | `notebooks/` (chạy trên Colab) | Huấn luyện, E0–E6, xuất `export/` | Chạy trong backend; là nơi agent sửa số liệu |
| Artifacts | `artifacts/` (copy tay từ Drive, không commit) | Model, đồ thị demo, mẫu JSON, bảng, hình | Bị sửa bởi mã trong repo |
| Nạp | `backend/app/core/registry.py` | Nạp artifacts **một lần** trong `lifespan` | Đọc file trong từng request |
| Dịch vụ | `backend/app/services/` | Cắt thời gian, suy luận, đọc bảng kết quả | Huấn luyện; tự tính lại số liệu thực nghiệm |
| API | `backend/app/api/` | REST `/api/*` theo README §4 | Nhận URL/văn bản tin tức mới; endpoint huấn luyện |
| Giao diện | `frontend/` | Explorer, GraphDetail, Results, DataReliability, About | Gọi gì khác ngoài `/api/*`; hard-code số liệu |

Chiều phụ thuộc chỉ đi một hướng:

```text
notebook (Colab) -> Drive export/ -> artifacts/ -> registry -> services -> /api/* -> frontend
```

Không có mũi tên ngược: backend không ghi vào `artifacts/`, frontend không đọc `artifacts/`
trực tiếp.

## Quy tắc bất biến

1. **Không sửa `artifacts/**`**, kể cả `artifacts/models/gnn_model.py` (sinh tự động). Đổi kiến
   trúc model thì đổi trong notebook, chạy lại §10 và copy lại artifacts.
2. **Không bịa số liệu.** Không hard-code F1, accuracy, AUC, số đồ thị hay bất kỳ con số thực
   nghiệm nào trong mã, test (ngoài fixture giả có ghi rõ), tài liệu hay UI. Mọi số đi qua API
   từ `artifacts/`.
3. **`graph_ops.py` port đúng 1:1** `keep_nodes`, `cut_time`, `undirected` của notebook. Mọi
   thay đổi phải giữ `tests/test_parity.py` xanh (sai số ≤ 1e-4 so với
   `golden_predictions.json`).
4. **Phiên bản khớp model card.** `torch` và `torch_geometric` của backend khớp
   `model_card.json`; `scripts/check_artifacts.py` phải qua trước khi chạy backend. CPU là đủ.
5. **Nạp một lần.** Artifacts nạp trong `lifespan`; health check báo đúng tình trạng (thiếu
   file thì báo thiếu, không giả "ok").
6. **Nhãn lấy từ `label_map`** trong `model_card.json`. Không giả định chỉ số 0/1 nghĩa là
   thật/giả trong mã.
7. **Phạm vi đã chốt.** Không thêm chức năng nhận URL hay văn bản tin mới, không huấn luyện lại
   trong backend, không trình bày hệ thống như công cụ kiểm chứng tin thật. Xem
   `DATA_BOUNDARY.md` mục 1 và 2.
8. **Chuỗi giao diện nằm trong i18n** (`vi.json`, `en.json`), tiếng Việt mặc định. Diễn giải
   kết quả do nhóm viết trong `frontend/src/content/results.md`; agent chỉ để placeholder.
9. **Footer mọi trang có câu miễn trừ**: *"Hệ thống minh họa cho đồ án học thuật, chỉ chạy
   trên dữ liệu UPFD đã công bố. Kết quả không phải là kết luận kiểm chứng thông tin."*
10. **Không phụ thuộc CDN ngoài khi build** (font, icon, thư viện tự host qua npm).
11. **Không có bí mật trong git.** `.env`, `artifacts/**` bị bỏ qua và phải giữ như vậy.
12. **Không chắc thì hỏi bằng văn bản.** Ghi câu hỏi vào `docs/open_questions.md` thay vì tự mở
    rộng hay thu hẹp phạm vi.
13. **Luôn cập nhật `BACKLOG.md` và README §9 khi xong một việc**, trong cùng commit/PR:
    đổi trạng thái task; việc phát sinh thì thêm dòng mới với mã kế tiếp (`O-3`…) trước khi
    làm.

## Khi sửa X thì cập nhật Y

| Sửa | Cập nhật cùng PR |
| --- | --- |
| Thêm/đổi endpoint | `backend/app/schemas/`, `tests/test_api.py`, bảng API trong README §4, `docs/api.md` |
| `services/graph_ops.py`, `services/inference.py` | `tests/test_parity.py` phải xanh; ghi rõ ô notebook tương ứng trong docstring |
| Cấu trúc `artifacts/` mong đợi | `scripts/check_artifacts.py`, README §2, `DATA_BOUNDARY.md` mục 3 |
| Biến môi trường mới | `.env.example`, `backend/app/core/config.py`, `docker-compose.yml` (khi có) |
| Phiên bản torch / pyg | Chỉ theo `model_card.json` mới; cập nhật `backend/pyproject.toml` |
| Trang/route giao diện | `DATA_BOUNDARY.md` mục 5, `vi.json` + `en.json` |
| Thêm thành phần kiến trúc | `docs/architecture.md` |
| Xong / dở một task | `BACKLOG.md`, README §9 |

## Kiểm tra trước khi xong

```bash
python scripts/run.py lint     # ruff + black --check (Windows không cần make)
python scripts/run.py test     # pytest backend
python scripts/run.py check    # scripts/check_artifacts.py (cần artifacts/)
# trên Linux/WSL/CI: make lint | make test | make check
```

- Test không cần artifacts thật: dùng fixture tạm trong `backend/tests/`. Riêng
  `test_parity.py` cần artifacts và tự `skip` khi thiếu, có ghi lý do.
- Không đánh dấu task là xong khi test đỏ hoặc frontend chưa build được.

## Quy ước

- Nhánh `<type>/<ID>-<mo-ta-ngan>`, commit Conventional Commits với scope là mã task hoặc
  `backend`/`frontend` (`feat(P1-1): nạp model card trong lifespan`). Chi tiết ở
  `CONTRIBUTING.md`.
- Tài liệu, comment, thông báo lỗi cho người dùng, commit: **tiếng Việt có dấu**. Tên biến,
  hàm, khoá cấu hình, tên endpoint: tiếng Anh.
- Máy phát triển chạy Windows: dùng `python scripts/run.py …` thay cho `make`.
- Skill giao diện (`.claude/skills/impeccable`, `.claude/skills/ui-ux-pro-max`) là mã bên thứ
  ba, chỉ dùng khi làm frontend (P3–P4); không sửa, không lint. `.claude/` bị `.gitignore`,
  không đưa lên repo: mỗi máy tự chép skill vào `.claude/skills/`.

## Thứ tự triển khai

1. P0: khung repo, quy ước, `check_artifacts.py`.
2. P1: registry + `graph_ops` + inference, parity test xanh; router health/models/graphs/predict.
3. P2: router results.
4. P3–P4: frontend, các trang còn lại, Docker.
5. P5: nghiệm thu theo README §8, video, tag `v1.0.0`.

P0 → P1 → P2 bắt buộc xong trước khi làm frontend (README §6).
