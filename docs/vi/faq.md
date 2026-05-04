# FAQ

Các câu hỏi thường gặp.

---

## Cài đặt

### Q: Làm sao để cài uv?

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Q: Có thể dùng công cụ khác thay cho uv không?

Có, bạn có thể dùng cách truyền thống là pip + venv.

---

## Cấu hình

### Q: Có bắt buộc phải cấu hình ComfyUI không?

**Không nhất thiết** — phụ thuộc vào template bạn chọn:

| Loại template | ComfyUI | Phù hợp với | Tốc độ |
|--------------|---------|----------|-------|
| Chỉ chữ<br/>(ví dụ `simple.html`) | ❌ Không cần | Trích dẫn, thông báo, đọc prompt | ⚡⚡⚡ Rất nhanh |
| Ảnh AI<br/>(ví dụ `default.html`) | ✅ Bắt buộc | Nội dung trực quan phong phú | ⚡ Tiêu chuẩn |

**Mẹo**: Người mới có thể bắt đầu với template chỉ chữ để trải nghiệm ngay không rào cản!

**Phương án thay thế**: Nếu bạn cần ảnh AI nhưng không muốn ComfyUI cục bộ, hãy dùng dịch vụ cloud RunningHub.

### Q: Hỗ trợ những LLM nào?

Tất cả LLM tương thích OpenAI, bao gồm:
- Qwen
- GPT-4o
- DeepSeek
- Ollama (cục bộ)

---

## Sử dụng

### Q: Lần đầu sử dụng mất bao lâu?

Tạo một video 3–5 cảnh mất khoảng 2–5 phút.

### Q: Nếu video chưa ưng ý thì sao?

Hãy thử:
1. Đổi model LLM
2. Chỉnh kích thước ảnh và tiền tố prompt
3. Đổi workflow TTS
4. Thử template video khác

### Q: Chi phí thì sao?

- **Hoàn toàn miễn phí**: Ollama + ComfyUI cục bộ = 0$
- **Khuyến nghị**: Qwen + ComfyUI cục bộ ≈ 0,01–0,05$/video
- **Phương án cloud**: OpenAI + RunningHub (chi phí cao hơn)

---

## Khắc phục sự cố

### Q: Kết nối ComfyUI thất bại

1. Xác nhận ComfyUI đang chạy
2. Kiểm tra URL có chính xác không
3. Nhấn "Test Connection" trong giao diện Web

### Q: Gọi API LLM thất bại

1. Kiểm tra API Key có chính xác không
2. Kiểm tra kết nối mạng
3. Xem thông báo lỗi

---

## Câu hỏi khác

Có câu hỏi khác? Xem [Khắc phục sự cố](troubleshooting.md) hoặc tạo [Issue](https://github.com/AIDC-AI/Pixelle-Video/issues).
