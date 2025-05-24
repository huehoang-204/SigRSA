
# 🔐 Hệ Thống Truyền File An Toàn với Chữ Ký Số RSA

Hệ thống cho phép người dùng truyền file an toàn với tính năng chữ ký số RSA, giúp đảm bảo tính toàn vẹn và xác thực của dữ liệu.

## ✨ Tính Năng Chính

- 🔑 Tạo và quản lý cặp khóa RSA
- 📤 Upload file với chữ ký số
- ✅ Xác thực tính toàn vẹn file
- 📝 Ký số tự động cho file
- 🔍 Kiểm tra trạng thái chữ ký
- 📊 Quản lý file đã upload

## 🛠️ Công Nghệ Sử Dụng

- **Backend**: Python Flask
- **Database**: SQLAlchemy
- **Mã Hóa**: Thư viện Cryptography
- **Frontend**: Bootstrap 5, Font Awesome
- **Xác Thực**: SHA-256, RSA

## 📋 Yêu Cầu Hệ Thống

```
Python 3.11+
Các thư viện trong requirements.txt
```

## 🚀 Cài Đặt và Chạy

1. Cài đặt các thư viện cần thiết:
```bash
pip install -r requirements.txt
```

2. Chạy ứng dụng:
```bash
python main.py
```

Ứng dụng sẽ chạy tại địa chỉ: `http://0.0.0.0:5000`

## 💡 Hướng Dẫn Sử Dụng

1. **Tạo Khóa RSA**:
   - Truy cập trang Quản lý khóa
   - Nhấn "Tạo cặp khóa mới"
   - Tải xuống khóa công khai và khóa riêng tư

2. **Upload File**:
   - Chọn file cần upload
   - File sẽ được tự động ký số nếu có khóa RSA
   - Xem thông tin file và chữ ký trong trang Quản lý file

3. **Xác Thực File**:
   - Truy cập trang Quản lý file
   - Nhấn nút xác thực với file đã chọn
   - Kiểm tra kết quả xác thực

## 🔒 Bảo Mật

- Sử dụng mã hóa RSA 2048-bit
- Hash file với SHA-256
- Lưu trữ an toàn khóa và file
- Xác thực tự động

## 📁 Cấu Trúc Thư Mục

```
├── instance/                  # Thư mục chứa database
│   └── secure_transfer.db    # File database SQLite
├── keys/                     # Thư mục lưu trữ khóa
├── static/                   # Tài nguyên tĩnh
│   ├── css/                 # Thư mục CSS
│   │   └── style.css       # File CSS chính
│   └── js/                  # Thư mục JavaScript
│       └── main.js         # File JavaScript chính
├── templates/                # Thư mục template
│   ├── base.html           # Template cơ sở
│   ├── files.html          # Trang quản lý file
│   ├── index.html          # Trang chủ
│   ├── index_new.html      # Trang chủ mới
│   ├── keys.html           # Trang quản lý khóa
│   └── upload.html         # Trang upload file
├── uploads/                  # Thư mục lưu trữ file
├── app.py                    # Khởi tạo ứng dụng Flask
├── crypto_utils.py           # Tiện ích mã hóa
├── main.py                   # File chạy chính
├── models.py                 # Mô hình dữ liệu
├── routes.py                 # Định tuyến và xử lý request
├── requirements.txt          # Danh sách thư viện
└── README.md                 # Tài liệu hướng dẫn
```

## 🤝 Đóng Góp

Mọi đóng góp và phản hồi đều được chào đón! Hãy tạo issue hoặc pull request để cải thiện hệ thống.

## 📄 Giấy Phép

MIT License - Xem file LICENSE để biết thêm chi tiết.
