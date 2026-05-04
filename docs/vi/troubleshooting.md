# Khắc phục sự cố

Gặp vấn đề? Dưới đây là giải pháp cho các tình huống thường gặp.

---

## Sự cố cài đặt

### Cài đặt phụ thuộc thất bại

```bash
# Dọn cache
uv cache clean

# Cài lại
uv sync
```

---

## Sự cố cấu hình

### Kết nối ComfyUI thất bại

**Nguyên nhân có thể**:
- ComfyUI chưa chạy
- Cấu hình URL sai
- Tường lửa chặn

**Cách khắc phục**:
1. Xác nhận ComfyUI đang chạy
2. Kiểm tra cấu hình URL (mặc định `http://127.0.0.1:8188`)
3. Thử mở địa chỉ ComfyUI trên trình duyệt
4. Kiểm tra cấu hình tường lửa

### Gọi API LLM thất bại

**Nguyên nhân có thể**:
- API Key sai
- Vấn đề mạng
- Số dư không đủ

**Cách khắc phục**:
1. Kiểm tra API Key có chính xác không
2. Kiểm tra kết nối mạng
3. Xem chi tiết thông báo lỗi
4. Kiểm tra số dư tài khoản

---

## Sự cố khi tạo video

### Tạo video thất bại

**Nguyên nhân có thể**:
- File workflow bị hỏng
- Chưa tải model
- Không đủ tài nguyên

**Cách khắc phục**:
1. Kiểm tra file workflow có tồn tại không
2. Xác nhận ComfyUI đã tải các model cần thiết
3. Kiểm tra dung lượng đĩa và bộ nhớ

### Sinh ảnh thất bại

**Cách khắc phục**:
1. Kiểm tra ComfyUI có chạy đúng không
2. Thử chạy thủ công workflow trong ComfyUI
3. Kiểm tra cấu hình workflow

### Sinh TTS thất bại

**Cách khắc phục**:
1. Kiểm tra workflow TTS có chính xác không
2. Nếu dùng voice cloning, kiểm tra định dạng audio tham chiếu
3. Xem log lỗi

---

## Sự cố hiệu năng

### Tốc độ tạo video chậm

**Mẹo tối ưu**:
1. Dùng ComfyUI cục bộ (nhanh hơn cloud)
2. Giảm số lượng cảnh
3. Dùng LLM nhanh hơn (ví dụ Qwen)
4. Kiểm tra kết nối mạng

---

## Vấn đề khác

Vẫn còn sự cố?

1. Xem [GitHub Issues](https://github.com/AIDC-AI/Pixelle-Video/issues) của dự án
2. Tạo Issue mới mô tả sự cố của bạn
3. Đính kèm log lỗi và chi tiết cấu hình để được chẩn đoán nhanh

---

## Xem log

File log nằm ở thư mục gốc dự án:
- `api_server.log` — Log dịch vụ API
- `test_output.log` — Log kiểm thử
