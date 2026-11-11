# Câu hỏi mở

Ghi câu hỏi ở đây thay vì tự quyết phạm vi (`AGENTS.md` quy tắc 12). Trả lời xong thì ghi
quyết định, ngày, người quyết định và cập nhật tài liệu liên quan.

| # | Câu hỏi | Ảnh hưởng | Tạm thời | Trạng thái |
|---|---|---|---|---|
| 1 | Notebook `DACN2_tuan3-5.ipynb` chưa có trong repo. Có commit bản không output vào `notebooks/` không? | Không port 1:1 `keep_nodes`, `cut_time`, `undirected` được (P1-1) | `graph_ops.py` chưa viết | Mở |
| 2 | `model_card.json` ghi phiên bản torch / torch_geometric ở khoá nào? | `check_artifacts.py` so phiên bản | Nhận `versions.torch` / `versions.torch_geometric`, hoặc `torch` / `torch_geometric` / `pyg` ở cấp ngoài cùng; không thấy thì cảnh báo | Mở |
| 3 | So phiên bản: khớp đúng `2.x.y` hay bỏ hậu tố build (`+cpu`, `+cu121`)? | Chạy CPU với model huấn luyện trên GPU Colab | Bỏ hậu tố build, so phần còn lại | Mở |
| 4 | Một cặp dataset × feature có nhiều file `<conv>.pt` (E0 có 4 GNN). API `/api/predict` dùng model nào? | `inference.py`, trường `model` trong response | Chưa chọn; `check_artifacts.py` chỉ yêu cầu ít nhất một file mỗi cặp | Mở |
| 5 | `results.csv` và `tables/*.csv` khác nhau thế nào (bảng tổng hay bảng E0)? | Trang Results (P2-1, P4-1) | Đọc cả hai, không gộp | Mở |
| 6 | Đề cương (DCCT) mô tả phát hiện sớm **theo độ sâu quan sát d** (cắt cây bằng BFS), còn README §4–5 (chốt trong báo cáo tiến độ) dùng **theo thời gian** (giờ). Hệ thống minh họa theo cách nào, hay cả hai? | Thanh trượt, API timeline, trang Results (E3) | Theo README: thời gian `[0.5 … 168, null]` giờ | Mở |
| 7 | Định dạng `samples/<dataset>.json` notebook xuất ra (khoá `nodes`, `edges`, `t_rel_h`, `label` là số hay chữ)? | `services/samples.py`, Explorer, GraphDetail | Theo đề xuất ở `docs/api.md`; nhận `label` số (đổi bằng `label_map`) hoặc chữ | Mở |
| 8 | Hệ thống có cần đăng nhập không, và vai trò `user` khác khách thế nào? | Toàn bộ API trừ `/api/health` | Đã làm theo yêu cầu 12/11: hai tài khoản `admin` / `user` (`docs/accounts.md`); bắt buộc đăng nhập, `AUTH_REQUIRED=0` để tắt khi demo công khai | Mở |
| 9 | Tên file bảng trong `tables/`: bảng thực nghiệm có bắt đầu bằng `E0`…`E6` không, bảng độ tin cậy dữ liệu tên gì? | Chia bảng giữa trang Results và DataReliability | Bắt đầu bằng `E` + số → Results; còn lại (trừ `graph_meta`) → DataReliability | Mở |
| 10 | `t_rel_h` trong samples và `rt` trong đồ thị `.pt` có cùng đơn vị (giờ) và cùng gốc thời gian không? | Số node hiển thị theo mốc phải khớp số node model thấy khi suy luận | Coi là một; kiểm tra lại trong parity test (P1-1) | Mở |
