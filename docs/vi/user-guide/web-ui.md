# Hướng dẫn Web UI

Giới thiệu chi tiết các tính năng của giao diện Web Pixelle-Video.

---

## Bố cục giao diện

Giao diện Web sử dụng bố cục ba cột:

- **Panel trái**: Nhập nội dung và cài đặt audio
- **Panel giữa**: Cài đặt giọng đọc và hình ảnh
- **Panel phải**: Tạo video và xem trước
- **Sidebar**: Cấu hình hệ thống và FAQ

---

## Cấu hình hệ thống

Lần đầu sử dụng cần cấu hình LLM và dịch vụ sinh ảnh. Xem [Hướng dẫn cấu hình](../getting-started/configuration.md).

---

## Nhập nội dung

### Chế độ sinh

- **Sinh nội dung bằng AI**: Nhập chủ đề, AI tự sáng tác kịch bản
- **Kịch bản cố định**: Nhập trực tiếp kịch bản hoàn chỉnh

### Chế độ tách kịch bản cố định

Khi dùng chế độ kịch bản cố định, bạn có thể chọn cách tách nội dung:

- **Theo đoạn**: Tách bằng dòng trống, mỗi đoạn thành một cảnh
- **Theo dòng**: Tách bằng xuống dòng, mỗi dòng thành một cảnh
- **Theo câu**: Phát hiện thông minh ranh giới câu, mỗi câu thành một cảnh

### Nhạc nền

- Hỗ trợ nhạc có sẵn
- Hỗ trợ file nhạc tuỳ chỉnh

---

## Cài đặt giọng đọc

### Workflow TTS

- Chọn workflow TTS
- Hỗ trợ Edge-TTS, Index-TTS, …

### Audio tham chiếu

- Tải lên audio tham chiếu để voice cloning
- Hỗ trợ định dạng MP3 / WAV / FLAC

---

## Cài đặt hình ảnh

### Sinh ảnh / video

- Chọn workflow sinh media (ảnh hoặc video)
- Tinh chỉnh tiền tố prompt để điều khiển phong cách

### Template video

- **Thư viện xem trước Template**: Xem trước trực quan tất cả template có sẵn
- Hỗ trợ dọc (1080x1920) / ngang (1920x1080) / vuông (1080x1080)
- Loại template:
  - `static_*.html`: Template tĩnh (không cần media do AI sinh)
  - `image_*.html`: Template ảnh (cần ảnh do AI sinh)
  - `video_*.html`: Template video (cần video do AI sinh)

---

## Tạo video

Sau khi nhấn "Tạo video", hệ thống sẽ:

1. Sinh kịch bản video
2. Sinh ảnh / video cho từng cảnh
3. Tổng hợp giọng đọc thuyết minh
4. Ghép video cuối cùng

Tự động xem trước khi hoàn tất.

---

## FAQ

Sidebar tích hợp sẵn FAQ để tra cứu nhanh:

- Vấn đề cấu hình thường gặp
- Cách khắc phục khi tạo video thất bại
- Mẹo tối ưu hiệu năng
