# Quy ước làm việc

## Nhánh

- `main`: luôn chạy được, chỉ cập nhật qua Pull Request.
- Nhánh làm việc: `<type>/<ID>-<mo-ta-ngan>`, chữ thường, không dấu, nối bằng `-`.
  - `type` ∈ `feat`, `fix`, `docs`, `chore`, `exp`, `refactor`, `test`, `ci`
  - `ID` là mã task trong `BACKLOG.md` (tuỳ chọn với việc vặt)
  - Ví dụ: `chore/P0-1-khung-repo`, `feat/P1-1-registry`, `feat/P3-2-propagation-tree`

## Commit (Conventional Commits)

```
<type>(<scope>): <mô tả ngắn, thể mệnh lệnh>
```

- `type` như trên, thêm `perf`, `build`, `style`, `revert` khi cần.
- `scope` là mã task (`feat(P1-1): nạp model card trong lifespan`) hoặc `backend`/`frontend`.
- Commit nhỏ, mỗi commit một ý.

## Pull Request

1. Tạo nhánh từ `main` mới nhất.
2. Tiêu đề PR theo cùng format commit; mô tả theo template.
3. CI xanh: lint (ruff, black), test (pytest), quy ước tên nhánh/tiêu đề/commit.
4. Cập nhật `BACKLOG.md` và bảng tiến độ README §9.
5. Merge kiểu **Squash and merge**, xoá nhánh sau khi merge.

## Chạy kiểm tra cục bộ

```bash
python scripts/run.py setup    # lần đầu: tạo .venv, cài backend + công cụ dev, pre-commit
python scripts/run.py lint
python scripts/run.py test
```
