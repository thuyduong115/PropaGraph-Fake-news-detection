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
