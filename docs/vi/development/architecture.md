# Kiến trúc

Tổng quan kiến trúc kỹ thuật của Pixelle-Video.

---

## Kiến trúc lõi

Pixelle-Video sử dụng thiết kế kiến trúc phân lớp:

- **Lớp Web**: Giao diện Web Streamlit
- **Lớp Service**: Logic nghiệp vụ cốt lõi
- **Lớp ComfyUI**: Sinh ảnh và TTS

---

## Thành phần chính

### PixelleVideoCore

Class service lõi điều phối toàn bộ các sub-service.

### LLM Service

Chịu trách nhiệm gọi mô hình ngôn ngữ lớn để sinh kịch bản.

### Image Service

Chịu trách nhiệm gọi ComfyUI để sinh ảnh.

### TTS Service

Chịu trách nhiệm gọi ComfyUI để sinh giọng nói.

### Video Generator

Chịu trách nhiệm ghép video cuối cùng.

---

## Stack công nghệ

- **Backend**: Python 3.10+, AsyncIO
- **Web**: Streamlit
- **AI**: OpenAI API, ComfyUI
- **Cấu hình**: YAML
- **Công cụ**: uv (quản lý gói)

---

## Thông tin thêm

Tài liệu kiến trúc chi tiết sắp ra mắt.
