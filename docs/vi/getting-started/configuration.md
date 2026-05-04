# Cấu hình

Sau khi cài đặt, bạn cần cấu hình các dịch vụ để sử dụng Pixelle-Video.

---

## Cấu hình LLM

LLM (Mô hình ngôn ngữ lớn) được dùng để sinh kịch bản video.

### Chọn nhanh từ preset

1. Chọn một model preset từ menu:
   - Qwen (khuyến nghị, hiệu năng/giá tốt)
   - GPT-4o
   - DeepSeek
   - Ollama (cục bộ, hoàn toàn miễn phí)

2. Hệ thống sẽ tự động điền `base_url` và `model`

3. Nhấn 「🔑 Lấy API Key」 để đăng ký và lấy thông tin xác thực

4. Nhập API Key của bạn

---

## Cấu hình sinh ảnh / video

Có hai phương án:

### Triển khai cục bộ

Dùng dịch vụ ComfyUI cục bộ:

1. Cài đặt và khởi động ComfyUI
2. Nhập ComfyUI URL (mặc định `http://127.0.0.1:8188`)
3. Nhấn "Test Connection" để xác minh
4. (Tuỳ chọn) Nhập ComfyUI API Key (lấy tại [Comfy Platform](https://platform.comfy.org/profile/api-keys))

### Triển khai cloud (Khuyến nghị)

Dùng dịch vụ cloud RunningHub, không cần GPU cục bộ:

1. Đăng ký tài khoản RunningHub
2. Lấy API Key
3. Nhập API Key vào cấu hình
4. Cấu hình tuỳ chọn nâng cao (không bắt buộc):
   - **Concurrent Limit**: Đặt số lượng task chạy đồng thời (1–10, mặc định 1 cho tài khoản thường)
   - **Instance Type**: Chọn máy 24GB hoặc 48GB VRAM (48GB cho sinh video kích thước lớn)

---

## Lưu cấu hình

Sau khi điền đầy đủ các trường bắt buộc, nhấn nút "Lưu cấu hình".

Cấu hình sẽ được lưu vào file `config.yaml`.

---

## Bước tiếp theo

- [Bắt đầu nhanh](quick-start.md) — Tạo video đầu tiên của bạn
