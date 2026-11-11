# PropaGraph — ranh giới dữ liệu, phạm vi và số liệu

Trạng thái: tài liệu gốc cho mọi thay đổi chạm tới artifacts, số liệu, API hay trang giao diện
(12/11/2026). Khi tài liệu khác mâu thuẫn với file này hoặc README, sửa tài liệu kia và ghi
vào `docs/open_questions.md` nếu chưa rõ bên nào đúng.

```text
Colab notebook ──(§10 xuất)──► Drive export/ ──(copy tay)──► artifacts/  (read-only)
                                                                │
                              backend registry (nạp 1 lần) ◄────┘
                                │  /api/*  REST/JSON
                              frontend (React) ◄┘
```

Không có mũi tên nào đi ngược từ backend hay frontend về `artifacts/` hoặc notebook.

## 1. Các vùng dữ liệu và chủ sở hữu

| Vùng | Lưu ở | Ghi bởi (duy nhất) | Nguồn sự thật? | Sinh lại được? |
| --- | --- | --- | --- | --- |
| Thực nghiệm | `notebooks/DACN2_tuan3-5.ipynb` | Nhóm, trên Colab | Có: nguồn của mọi số liệu | — |
| Export | Drive `VKU-Study/DACN2/v2/export/` | Notebook §10 | Có, bản phát hành của notebook | Có: chạy lại notebook |
| Artifacts | `artifacts/` (không commit) | Người copy tay từ Drive | Không: bản sao của export | Có: copy lại |
| Bộ nhớ backend | `app.state.registry` | `core/registry.py` lúc khởi động | Không: dẫn xuất | Có: khởi động lại |
| Giao diện | trình duyệt | — | Không | — |
| Diễn giải kết quả | `frontend/src/content/results.md` | Nhóm (người), qua PR | Có: lời của nhóm | — |

Quy tắc rút ra:

- Mã trong repo không ghi vào `artifacts/`. Sai số liệu thì sửa notebook và xuất lại.
- Không có cơ sở dữ liệu, hàng đợi hay bộ nhớ đệm lâu dài. Cache trong RAM chỉ dẫn xuất từ
  artifacts đã nạp.
- Diễn giải kết quả là lời của nhóm. Agent không viết, không sinh tự động.

## 2. Phạm vi sản phẩm

| Làm | Không làm |
| --- | --- |
| Duyệt cây lan truyền mẫu (200 đồ thị test / tập, cân bằng nhãn) của PolitiFact, GossipCop | Nhận URL, văn bản hay đồ thị tin tức mới |
| Hiển thị cây: bố cục cây/radial, màu theo thời gian, kích thước theo bậc | Huấn luyện hay tinh chỉnh model trong backend |
| Dự đoán thật/giả kèm xác suất bằng model GNN đã huấn luyện | Kiểm chứng tin tức thực tế |
| Mô phỏng phát hiện sớm theo mốc thời gian | Crawl Twitter hay tính lại đặc trưng user |
| Trang kết quả thực nghiệm và độ tin cậy dữ liệu, đọc từ artifacts | Tự tính, làm tròn lại hay "làm đẹp" số liệu notebook |

Lý do không nhận tin mới: UPFD không có văn bản gốc, và đặc trưng user được tính từ lịch sử
tweet không còn crawl được.

## 3. Artifacts mong đợi

Kiểm tra bằng `python scripts/check_artifacts.py`. Thiếu file bắt buộc là lỗi, không phải cảnh
báo.

| Đường dẫn | Bắt buộc | Dùng ở |
| --- | --- | --- |
| `models/gnn_model.py` | Có | `registry` (định nghĩa model, sinh tự động) |
| `models/model_card.json` | Có | `/api/models`, `/api/health`, `label_map`, phiên bản |
| `models/golden_predictions.json` | Có | `tests/test_parity.py` |
| `models/<dataset>_<feature>_<conv>.pt` | Có, mỗi cặp dataset × feature ít nhất một | `services/inference.py` |
| `graphs/<dataset>_<feature>_demo.pt` | Có, cho 2 dataset × 2 feature | `services/inference.py` |
| `samples/<dataset>.json` | Có, cho 2 dataset | `/api/datasets/{ds}/graphs*` |
| `tables/graph_meta.csv` | Có | metadata đồ thị |
| `tables/*.csv` | Có (ít nhất một) | `/api/results/tables` |
| `results.csv` | Có | trang Results |
| `figs/*.png` | Không (cảnh báo nếu trống) | `/api/results/figures` |

Dataset: `politifact`, `gossipcop`. Feature: `profile`, `bert`.

## 4. API namespace

Mọi endpoint nằm dưới `/api`. Bảng đầy đủ ở README §4; mỗi endpoint chỉ đọc.

| Được phép | Không được thêm |
| --- | --- |
| `GET /api/health`, `/api/models`, `/api/datasets*`, `/api/results*` | Endpoint nhận URL/văn bản tin tức |
| `POST /api/predict` trên `gid` có sẵn trong đồ thị demo | Endpoint huấn luyện, upload model hay upload đồ thị |
| | Endpoint ghi vào `artifacts/` |

`POST /api/predict` là phép tính, không phải thao tác ghi. Nó chỉ nhận `{dataset, gid,
feature, cutoff_h}`; `gid` ngoài tập demo trả `404`.

## 5. Trang giao diện

| Route | Trang | Nguồn số liệu |
| --- | --- | --- |
| `/` | Explorer | `/api/datasets/{ds}/graphs` |
| `/graphs/:ds/:gid` | GraphDetail | `/api/datasets/{ds}/graphs/{gid}`, `/timeline`, `/api/predict` |
| `/results` | Results | `/api/results/*` + diễn giải trong `content/results.md` |
| `/data-reliability` | DataReliability | phát hiện ở notebook §1 qua `/api/results/*` |
| `/about` | About | phương pháp, nhóm, miễn trừ |

Route cụ thể được chốt ở P3; đổi route thì cập nhật bảng này.

## 6. Một con số được phép khẳng định gì

- Mọi số liệu là kết quả **trên tập test UPFD** (PolitiFact hoặc GossipCop), ghi rõ tập nào.
- Xác suất trên GraphDetail là đầu ra của model trên đồ thị demo, không phải "mức độ tin giả"
  của bài báo ngoài đời.
- PolitiFact có nhiễu thời gian (notebook §1); kết luận chính về phát hiện sớm dựa trên
  GossipCop. Giao diện và báo cáo không đảo thứ tự này.
- Không gộp số của paper UPFD (Dou et al., 2021) vào bảng như kết quả của đề tài; nếu so sánh,
  ghi nguồn.

## 7. Các điểm dễ hiểu sai và quyết định

| Điểm | Quyết định |
| --- | --- |
| `cutoff_h = null` | Dùng toàn bộ cây. |
| Mốc thời gian của timeline | Cố định `[0.5, 1, 3, 6, 12, 24, 72, 168, null]` (README §4); một lần gọi cho cả thanh trượt. |
| User mất cha khi cắt thời gian | Nối lại vào gốc (`keep_nodes`), đúng như notebook. |
| Chỉ số node và thời gian | Chỉ số node không phải thứ tự thời gian; thời gian lấy từ `t_rel_h` / `rt`. |
| Nghĩa của lớp 0/1 | Theo `label_map` trong `model_card.json`, đã đối chiếu FakeNewsNet ở notebook §1.1. |
| Đặc trưng `x` | Lưu float16 trong `.pt`, đổi sang float32 trước khi suy luận. |
| Nhiều model `<conv>` cho cùng dataset × feature | Chưa chốt model nào được dùng: xem `docs/open_questions.md`. |

## 8. Tiêu chí nghiệm thu ranh giới

1. `scripts/check_artifacts.py` báo lỗi rõ khi thiếu file hoặc lệch phiên bản.
2. Không file mã nào ghi vào `artifacts/`.
3. Không con số thực nghiệm nào xuất hiện trong mã nguồn hay chuỗi i18n.
4. Footer mọi trang có câu miễn trừ.
5. Không endpoint nào nhận dữ liệu tin tức mới.
6. `tests/test_parity.py` xanh trên artifacts hiện hành.
