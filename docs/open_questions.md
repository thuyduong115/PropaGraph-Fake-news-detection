# Câu hỏi mở

Ghi câu hỏi ở đây thay vì tự quyết phạm vi (`AGENTS.md` quy tắc 12). Trả lời xong thì ghi
quyết định, ngày, người quyết định và cập nhật tài liệu liên quan.

| # | Câu hỏi | Ảnh hưởng | Tạm thời | Trạng thái |
|---|---|---|---|---|
| 1 | Notebook chưa có trong repo. Có commit bản không output vào `notebooks/` không? | Port 1:1 `graph_ops` (P1-1) | `notebooks/DACN2_v2.ipynb` chỉ giữ trên máy, bị `.gitignore`; `graph_ops.py` port từ §3 | Đã chốt 12/11: không commit notebook (nhóm) |
| 2 | `model_card.json` ghi phiên bản torch / torch_geometric ở khoá nào? | `check_artifacts.py` so phiên bản | Notebook §10: `torch`, `torch_geometric` ở cấp ngoài của từng mục trong danh sách | Đã chốt 12/11 theo export |
| 3 | So phiên bản: khớp đúng `2.x.y` hay bỏ hậu tố build (`+cpu`, `+cu121`)? | Chạy CPU với model huấn luyện trên GPU Colab | Bỏ hậu tố build, so phần còn lại | Mở |
| 4 | Một cặp dataset × feature có nhiều file `<conv>.pt` (E0 có 4 GNN). API `/api/predict` dùng model nào? | `inference.py`, trường `model` trong response | Notebook §10 chỉ xuất GNN có F1 trung bình E0 cao nhất cho mỗi cặp (seed 0), ghi ở mục `file` của model card | Đã chốt 12/11 theo export |
| 5 | `results.csv` và `tables/*.csv` khác nhau thế nào (bảng tổng hay bảng E0)? | Trang Results (P2-1, P4-1) | Đọc cả hai, không gộp | Mở |
| 6 | Đề cương (DCCT) mô tả phát hiện sớm **theo độ sâu quan sát d** (cắt cây bằng BFS), còn README §4–5 (chốt trong báo cáo tiến độ) dùng **theo thời gian** (giờ). Hệ thống minh họa theo cách nào, hay cả hai? | Thanh trượt, API timeline, trang Results (E3) | Theo README: thời gian `[0.5 … 168, null]` giờ | Mở |
| 7 | Định dạng `samples/<dataset>.json` notebook xuất ra (khoá `nodes`, `edges`, `t_rel_h`, `label` là số hay chữ)? | `services/samples.py`, Explorer, GraphDetail | Danh sách trực tiếp; `label` là chữ (`fake`/`real`); khớp `docs/api.md` | Đã chốt 12/11 theo export |
| 8 | Hệ thống có cần đăng nhập không, và vai trò `user` khác khách thế nào? | Toàn bộ API trừ `/api/health` | Đã làm theo yêu cầu 12/11: hai tài khoản `admin` / `user` (`docs/accounts.md`); bắt buộc đăng nhập, `AUTH_REQUIRED=0` để tắt khi demo công khai | Mở |
| 9 | Tên file bảng trong `tables/`: bảng thực nghiệm có bắt đầu bằng `E0`…`E6` không, bảng độ tin cậy dữ liệu tên gì? | Chia bảng giữa trang Results và DataReliability | Bắt đầu bằng `E` + số → Results; còn lại (trừ `graph_meta`) → DataReliability | Mở |
| 10 | `t_rel_h` trong samples và `rt` trong đồ thị `.pt` có cùng đơn vị (giờ) và cùng gốc thời gian không? | Số node hiển thị theo mốc phải khớp số node model thấy khi suy luận | Cùng công thức ở notebook §3/§10; `test_parity.py` kiểm tra số node khớp trên 240 ca golden | Đã kiểm 12/11 |
