# API

Tài liệu tương tác (OpenAPI) tại `http://localhost:8000/docs` khi backend chạy. Mọi endpoint
nằm dưới `/api`, chỉ đọc artifacts. Đăng nhập và quyền: [`accounts.md`](accounts.md).

## Endpoint

| Method | Path | Quyền | Mô tả | Trạng thái |
| --- | --- | --- | --- | --- |
| GET | `/api/health` | công khai | `status` (`ok`/`degraded`), phiên bản torch/pyg, model đã nạp, `synthetic`, `problems`, `notes` | xong |
| POST | `/api/auth/login` | công khai | body `{username, password}` → đặt cookie phiên, trả `{username, role, auth_required}` | xong |
| POST | `/api/auth/logout` | công khai | xoá cookie, 204 | xong |
| GET | `/api/auth/me` | user | tài khoản hiện tại | xong |
| GET | `/api/models` | user | nguyên văn `model_card.json`; 503 khi chưa có | xong (chờ model card) |
| GET | `/api/datasets` | user | `[{name, n_graphs, labels}]` | xong |
| GET | `/api/datasets/{ds}/graphs` | user | danh sách tóm tắt; query `label`, `min_nodes`, `max_nodes`, `q`, `sort` (`gid`, `n_nodes`, `depth`, `span_h`, thêm `-` để giảm dần), `page`, `size` (≤ 200) | xong |
| GET | `/api/datasets/{ds}/graphs/{gid}` | user | cây đầy đủ: `nodes[{id, depth, t_rel_h}]`, `edges[[src, dst]]` + tóm tắt | xong |
| GET | `/api/datasets/{ds}/graphs/{gid}/timeline?feature=` | user | mọi mốc `[0.5, 1, 3, 6, 12, 24, 72, 168, null]`: `n_nodes_used`, `prob_fake` (`null` khi chưa có model), `model_ready` | xong phần số node; xác suất chờ P1-1 |
| POST | `/api/predict` | user | body `{dataset, gid, feature, cutoff_h}` → `{prob_fake, pred_label, n_nodes_used, n_nodes_total, model}`; **503** khi chưa có model | chờ P1-1 |
| GET | `/api/results/tables?group=` | user | `[{name, group, n_rows}]`; `group` ∈ `experiment`, `reliability`, `summary`, `meta` | xong |
| GET | `/api/results/tables/{name}` | user | `{columns, rows}`, giá trị giữ nguyên chuỗi trong CSV | xong |
| GET | `/api/results/figures` | user | `[{name, url}]` | xong |
| GET | `/api/results/figures/{name}` | user | ảnh PNG | xong |
| GET | `/api/admin/status` | admin | thư mục artifacts, thời điểm nạp, số đồ thị, bảng, hình, model | xong |
| POST | `/api/admin/reload` | admin | nạp lại artifacts từ đĩa (không ghi gì) | xong |

Mã lỗi: `401` chưa đăng nhập, `403` sai vai trò, `404` dataset/gid/bảng/hình không có, `422`
tham số sai, `503` model hoặc model card chưa có.

## Tóm tắt đồ thị

`GraphSummary`: `gid, news_id, title, label, n_nodes, depth, span_h, growth`.

- `depth`: độ sâu lớn nhất; `span_h`: `t_rel_h` lớn nhất (giờ).
- `growth[i]`: số node nhìn thấy tại mốc thứ `i` của timeline (gốc luôn tính), dùng cho
  sparkline ở Explorer.
- `label`: nếu `samples` lưu số và model card có `label_map` thì đổi sang chữ; ngược lại giữ
  nguyên giá trị trong file.

## Định dạng `samples/<dataset>.json`

Notebook §10 xuất theo định dạng này (đề xuất, chờ nhóm xác nhận: `open_questions.md` #7):

```json
{
  "dataset": "gossipcop",
  "graphs": [
    {
      "gid": 0,
      "news_id": "gossipcop-123456",
      "title": "Tiêu đề bản tin",
      "label": 1,
      "nodes": [
        { "id": 0, "depth": 0, "t_rel_h": 0.0 },
        { "id": 1, "depth": 1, "t_rel_h": 0.42 }
      ],
      "edges": [[0, 1]]
    }
  ]
}
```

- Chấp nhận cả danh sách đồ thị trực tiếp (không có object bọc ngoài).
- `nodes[].t_rel_h`: giờ kể từ bài gốc; `null` nếu không rõ (node đó chỉ hiện ở mốc "toàn
  bộ"). Nút gốc có `depth = 0`.
- `edges`: cặp `[cha, con]`; node không có cha được treo vào gốc khi vẽ.
- Khoá `"synthetic": true` ở cấp ngoài cùng đánh dấu dữ liệu giả
  (`scripts/make_dev_artifacts.py`); giao diện hiện cảnh báo. Bản export thật không có khoá này.

## Nhóm bảng kết quả

Theo tên file trong `tables/` (`services/results.py`):

| Tên | Nhóm | Trang |
| --- | --- | --- |
| bắt đầu bằng `E` + số (`E0_…`, `E3_…`) | `experiment` | Kết quả |
| `results` (`results.csv`) | `summary` | Kết quả |
| `graph_meta` | `meta` | không hiển thị |
| còn lại | `reliability` | Độ tin cậy dữ liệu |
