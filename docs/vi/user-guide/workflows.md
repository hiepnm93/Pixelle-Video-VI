# Tuỳ biến Workflow

Cách tuỳ biến workflow ComfyUI để đạt được chức năng mong muốn.

---

## Giới thiệu Workflow

Pixelle-Video được xây dựng trên kiến trúc ComfyUI và hỗ trợ workflow tuỳ chỉnh.

---

## Các loại Workflow

### Workflow TTS

Nằm trong `workflows/selfhost/` hoặc `workflows/runninghub/`

Dùng cho Text-to-Speech, hỗ trợ nhiều engine TTS:
- Edge-TTS
- Index-TTS (hỗ trợ voice cloning)
- Các node TTS khác tương thích ComfyUI

### Workflow sinh ảnh

Nằm trong `workflows/selfhost/` hoặc `workflows/runninghub/`

Dùng để sinh ảnh tĩnh làm nền cho video:
- Các model dòng FLUX
- Các model dòng Stable Diffusion
- Các model sinh ảnh khác

### Workflow sinh video

Nằm trong `workflows/selfhost/` hoặc `workflows/runninghub/`

**Tính năng mới**: Hỗ trợ sinh video bằng AI để tạo nội dung video động.

**Workflow có sẵn**:
- `runninghub/video_wan2.1_fusionx.json`: Workflow cloud (khuyến nghị)
  - Dựa trên model WAN 2.1
  - Không cần thiết lập cục bộ, truy cập qua API RunningHub
  - Hỗ trợ sinh Text-to-Video
  
- `selfhost/video_wan2.1_fusionx.json`: Workflow cục bộ
  - Cần môi trường ComfyUI cục bộ
  - Cần cài các node sinh video tương ứng
  - Phù hợp với người có GPU cục bộ

**Tình huống sử dụng**:
- Hoạt động cùng template `video_*.html`
- Tự động sinh nền video động dựa trên kịch bản
- Tăng tính biểu cảm và trải nghiệm xem

---

## Workflow tuỳ chỉnh

1. Thiết kế workflow của bạn trong ComfyUI
2. Xuất ra file JSON
3. Đặt vào thư mục `workflows/`
4. Chọn và sử dụng trong giao diện Web

---

## Thông tin thêm

Hướng dẫn chi tiết về tuỳ biến workflow sẽ được bổ sung sau.
