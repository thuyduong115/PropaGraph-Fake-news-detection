# Tải artifacts về máy

Artifacts không nằm trong git. Mỗi lần notebook xuất lại (§10), làm như sau:

1. Mở Google Drive, thư mục `VKU-Study/DACN2/v2/export/`.
2. Tải cả thư mục (Drive nén thành `.zip`).
3. Giải nén sao cho cấu trúc là:

   ```text
   artifacts/
   ├── models/   (gnn_model.py, model_card.json, golden_predictions.json, *.pt)
   ├── graphs/   (<dataset>_<feature>_demo.pt)
   ├── samples/  (<dataset>.json)
   ├── tables/   (*.csv, graph_meta.csv)
   ├── figs/     (*.png)
   └── results.csv
   ```

   Không để thừa một cấp `artifacts/export/…`.
4. Kiểm tra:

   ```bash
   python scripts/check_artifacts.py
   ```

   Lệnh trả mã 0 khi đủ file và phiên bản torch/pyg đang cài khớp `model_card.json`. Chỉ muốn
   kiểm tra file (chưa cài torch): `python scripts/check_artifacts.py --skip-versions`.

Không sửa file nào trong `artifacts/`. Sai thì sửa notebook và xuất lại.
