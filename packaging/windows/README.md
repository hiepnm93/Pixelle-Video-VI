# Windows Package Builder

Hệ thống build tự động dùng để tạo gói portable Windows cho Pixelle-Video.

## Bắt đầu nhanh

### Yêu cầu trước khi cài

- Python 3.11+ (để chạy script build)
- PyYAML: `pip install pyyaml`
- Kết nối Internet (để tải Python, FFmpeg, v.v.)

### Build gói

```bash
# Build cơ bản
python packaging/windows/build.py

# Build dùng mirror Trung Quốc (nhanh hơn ở TQ)
python packaging/windows/build.py --cn-mirror

# Tuỳ chỉnh thư mục output
python packaging/windows/build.py --output /path/to/output
```

## Cấu hình

Chỉnh sửa `config/build_config.yaml` để tuỳ chỉnh:

- Phiên bản Python
- Phiên bản FFmpeg
- File/thư mục bị loại trừ
- Tuỳ chọn build
- Cài đặt mirror

## Output

Quá trình build sẽ tạo ra:

```
dist/windows/
├── Pixelle-Video-v*-win64/             # Thư mục build (số phiên bản thay đổi)
│   ├── python/                         # Python embedded
│   ├── tools/                          # FFmpeg, v.v.
│   ├── Pixelle-Video/                  # File của dự án
│   ├── data/                           # Dữ liệu người dùng (rỗng)
│   ├── output/                         # Output (rỗng)
│   ├── start.bat                       # Launcher chính
│   ├── start_api.bat                   # Launcher API
│   ├── start_web.bat                   # Launcher Web
│   └── README.txt                      # Hướng dẫn người dùng
├── Pixelle-Video-v*-win64.zip          # Gói ZIP (số phiên bản thay đổi)
└── Pixelle-Video-v*-win64.zip.sha256   # Checksum (số phiên bản thay đổi)
```

## Quy trình build

Builder thực hiện các bước sau:

1. **Giai đoạn tải**
   - Bản phân phối Python embedded
   - FFmpeg portable
   - Cache lại trong `.cache/` để tái sử dụng

2. **Giai đoạn giải nén**
   - Giải nén Python vào `build/python/`
   - Giải nén FFmpeg vào `build/tools/ffmpeg/`

3. **Giai đoạn chuẩn bị**
   - Bật site-packages trong Python
   - Cài pip
   - Cài uv (nếu được cấu hình)

4. **Giai đoạn cài đặt**
   - Cài các dependency của dự án bằng uv/pip
   - Cài trước toàn bộ package

5. **Giai đoạn copy**
   - Copy file dự án (loại trừ test/docs/cache)
   - Tạo các script launcher từ template
   - Tạo các thư mục rỗng

6. **Giai đoạn đóng gói**
   - Tạo file ZIP
   - Tạo checksum SHA256

## Templates

Các template script launcher trong `templates/`:

- `start.bat` - Launcher Web UI chính
- `start_api.bat` - Launcher API server
- `start_web.bat` - Launcher chỉ chạy Web UI
- `README.txt` - Tài liệu cho người dùng

Template hỗ trợ các placeholder:
- `{VERSION}` - Phiên bản dự án
- `{BUILD_DATE}` - Timestamp build

## Cache

Các file đã tải được cache trong `.cache/`:

```
.cache/
├── python-3.11.9-embed-amd64.zip
├── ffmpeg-6.1.1-win64.zip
└── get-pip.py
```

Xoá cache để bắt buộc tải lại.

## Khắc phục sự cố

### Build báo "PyYAML not found"

```bash
pip install pyyaml
```

### Tải xuống chậm

Dùng mirror Trung Quốc:

```bash
python build.py --cn-mirror
```

### Cài dependency thất bại

Kiểm tra:
1. Kết nối Internet
2. Có vào được mirror PyPI không
3. Các dependency dự án trong `pyproject.toml`

### Tạo ZIP thất bại

Đảm bảo:
1. Đủ dung lượng đĩa
2. Có quyền ghi vào thư mục output
3. Không có file nào đang bị process khác khoá

## Sử dụng nâng cao

### Cấu hình tuỳ chỉnh

Tạo file cấu hình tuỳ chỉnh:

```bash
cp config/build_config.yaml config/my_config.yaml
# Chỉnh sửa my_config.yaml
python build.py --config config/my_config.yaml
```

### Bỏ qua bước tạo ZIP

Chỉnh `build_config.yaml`:

```yaml
build:
  create_zip: false
```

### Bao gồm Chrome Portable

Chỉnh `build_config.yaml`:

```yaml
chrome:
  include: true
  download_url: "https://path/to/chrome-portable.zip"
```

## Bảo trì

### Cập nhật phiên bản Python

Chỉnh `config/build_config.yaml`:

```yaml
python:
  version: "3.11.10"
  download_url: "https://www.python.org/ftp/python/3.11.10/python-3.11.10-embed-amd64.zip"
```

### Cập nhật phiên bản FFmpeg

Chỉnh `config/build_config.yaml`:

```yaml
ffmpeg:
  version: "6.2.0"
  download_url: "https://github.com/BtbN/FFmpeg-Builds/releases/download/..."
```

## Phân phối

Để phân phối gói:

1. Upload file ZIP lên trang release
2. Đính kèm checksum SHA256 để xác minh
3. Cung cấp hướng dẫn cài đặt

Người dùng xác minh file đã tải:

```bash
# Windows PowerShell
Get-FileHash Pixelle-Video-v*-win64.zip -Algorithm SHA256
```

So sánh với file `.sha256`.

## Giấy phép

Giống với giấy phép của dự án Pixelle-Video.

