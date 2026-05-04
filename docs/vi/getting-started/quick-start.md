# Bắt đầu nhanh

Đã cài đặt và cấu hình xong? Cùng tạo video đầu tiên của bạn nào!

---

## Khởi động giao diện Web

### Người dùng bản Windows All-in-One

Nếu bạn dùng bản Windows All-in-One, chỉ cần:
1. Nháy đúp vào `start.bat`
2. Trình duyệt sẽ tự động mở `http://localhost:8501`

### Người cài từ mã nguồn

```bash
# Dùng uv
uv run streamlit run web/app.py
```

Trình duyệt sẽ tự động mở `http://localhost:8501`

---

## Tạo video đầu tiên

### Bước 1: Kiểm tra cấu hình

Lần đầu sử dụng, mở rộng panel 「⚙️ Cấu hình hệ thống」 và xác nhận:

- **Cấu hình LLM**: Chọn model AI (ví dụ Qwen, GPT) và nhập API Key
- **Cấu hình hình ảnh**: Cấu hình địa chỉ ComfyUI hoặc API Key của RunningHub

Nếu chưa cấu hình, xem [Hướng dẫn cấu hình](configuration.md).

Nhấn "Lưu cấu hình" khi xong.

---

### Bước 2: Nhập chủ đề

Trong panel bên trái, mục 「📝 Nhập nội dung」:

1. Chọn chế độ 「**Sinh nội dung bằng AI**」
2. Nhập chủ đề vào ô văn bản, ví dụ:
   ```
   Vì sao nên rèn luyện thói quen đọc sách
   ```
3. (Tuỳ chọn) Đặt số lượng cảnh, mặc định là 5 khung

!!! tip "Ví dụ chủ đề"
    - Vì sao nên rèn luyện thói quen đọc sách
    - Cách nâng cao hiệu suất công việc
    - Tầm quan trọng của ăn uống lành mạnh
    - Ý nghĩa của những chuyến du lịch

---

### Bước 3: Cấu hình giọng đọc và hình ảnh

Trong panel ở giữa:

**Cài đặt giọng đọc**
- Chọn workflow TTS (mặc định Edge-TTS hoạt động tốt)
- Để nhân bản giọng (voice cloning), tải lên file audio tham chiếu

**Cài đặt hình ảnh**
- Chọn workflow sinh ảnh (mặc định hoạt động tốt)
- Đặt kích thước ảnh (mặc định 1024x1024)
- Chọn template video (khuyến nghị dọc 1080x1920)

---

### Bước 4: Tạo video

Nhấn nút 「🎬 Tạo video」 ở panel bên phải!

Hệ thống sẽ hiển thị tiến độ thời gian thực:
- Sinh kịch bản
- Sinh ảnh (cho từng cảnh)
- Tổng hợp giọng nói
- Ghép video

!!! info "Thời gian tạo video"
    Tạo một video 5 cảnh mất khoảng 2–5 phút, phụ thuộc vào: tốc độ phản hồi của LLM API, tốc độ sinh ảnh, loại workflow TTS, và điều kiện mạng.

---

### Bước 5: Xem trước video

Khi hoàn tất, video sẽ tự động phát ở panel bên phải!

Bạn sẽ thấy:
- 📹 Trình phát xem trước video
- ⏱️ Thời lượng video
- 📦 Dung lượng file
- 🎬 Số lượng cảnh
- 📐 Kích thước video

File video được lưu trong thư mục `output/`.

---

## Bước tiếp theo

Chúc mừng! Bạn đã tạo thành công video đầu tiên 🎉

Tiếp theo, bạn có thể:

- **Tinh chỉnh phong cách** — Xem hướng dẫn [Tuỳ biến phong cách hình ảnh](../tutorials/custom-style.md)
- **Nhân bản giọng nói** — Xem hướng dẫn [Nhân bản giọng với audio tham chiếu](../tutorials/voice-cloning.md)
- **Dùng API** — Xem [Hướng dẫn dùng API](../user-guide/api.md)
- **Phát triển template** — Xem [Hướng dẫn phát triển template](../user-guide/templates.md)
