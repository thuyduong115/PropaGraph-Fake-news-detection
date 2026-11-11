# Tài khoản thử

Hệ thống có hai tài khoản cấu hình bằng biến môi trường. Không có bảng người dùng hay cơ sở dữ
liệu; phiên đăng nhập là cookie httpOnly ký HMAC (`backend/app/core/auth.py`).

## Tài khoản mặc định (phát triển và demo)

| Vai trò | Tên đăng nhập | Mật khẩu | Biến môi trường | Được làm gì |
| --- | --- | --- | --- | --- |
| Quản trị | `admin` | `admin@123` | `ADMIN_USERNAME`, `ADMIN_PASSWORD` | Mọi trang của người dùng + trang **Hệ thống** (`/admin`): xem tình trạng artifacts, nạp lại artifacts |
| Người dùng | `user` | `user@123` | `USER_USERNAME`, `USER_PASSWORD` | Đồ thị, chi tiết cây, dự đoán, Kết quả, Độ tin cậy dữ liệu, Giới thiệu |

Mật khẩu mặc định ở trên **chỉ dùng trên máy phát triển và buổi demo nội bộ**. Khi chạy ở nơi
người ngoài truy cập được, đổi cả hai mật khẩu và đặt `AUTH_SECRET` trong `.env`.

## Cấu hình liên quan

| Biến | Mặc định | Ý nghĩa |
| --- | --- | --- |
| `AUTH_REQUIRED` | `1` | `0` tắt đăng nhập: mọi người xem như vai trò `user`, trang Hệ thống vẫn chỉ cho `admin` |
| `AUTH_SECRET` | trống | Khoá ký phiên. Trống thì sinh ngẫu nhiên mỗi lần khởi động (phiên mất khi khởi động lại) |
| `SESSION_HOURS` | `12` | Thời hạn phiên |
| `COOKIE_SECURE` | `0` | Đặt `1` khi chạy sau HTTPS |

Đổi tên đăng nhập hoặc vai trò trong cấu hình làm các phiên cũ của tài khoản đó hết hiệu lực.

## Quyền theo endpoint

| Endpoint | Khách | `user` | `admin` |
| --- | --- | --- | --- |
| `GET /api/health`, `POST /api/auth/login` | có | có | có |
| `/api/datasets*`, `/api/predict`, `/api/results*`, `/api/models`, `/api/auth/me` | 401 | có | có |
| `/api/admin/*` | 401 | 403 | có |

Quyền kiểm tra ở backend (`api/deps.py`). Frontend chỉ ẩn menu và trang.
