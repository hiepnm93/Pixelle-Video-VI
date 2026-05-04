# Tổng quan API

Pixelle-Video cung cấp cả Python SDK và HTTP REST API.

---

## Python SDK

### PixelleVideoCore

Class service chính cung cấp chức năng sinh video.

```python
from pixelle_video.service import PixelleVideoCore

pixelle = PixelleVideoCore()
await pixelle.initialize()
```

### generate_video()

Phương thức chính để sinh video.

**Tham số**:

- `text` (str): Chủ đề hoặc kịch bản hoàn chỉnh
- `mode` (str): Chế độ sinh ("generate" hoặc "fixed")
- `n_scenes` (int): Số lượng cảnh
- `title` (str, tuỳ chọn): Tiêu đề video
- `tts_workflow` (str): Workflow TTS
- `media_workflow` (str): Workflow sinh media (ảnh hoặc video)
- `frame_template` (str): Template video
- `template_params` (dict, tuỳ chọn): Tham số tuỳ chỉnh cho template
- `bgm_path` (str, tuỳ chọn): Đường dẫn file BGM
- `bgm_volume` (float): Âm lượng BGM (0.0–1.0)

**Trả về**: Đối tượng `VideoResult`

---

## HTTP REST API

Khởi động API server:

```bash
uv run uvicorn api.app:app --host 0.0.0.0 --port 8000
```

### Sinh video — Đồng bộ

`POST /api/video/generate/sync`

Sinh video đồng bộ, chờ đến khi hoàn tất. Phù hợp với video ngắn (< 30 giây).

**Request Body**:

```json
{
  "text": "Why you should develop a reading habit",
  "mode": "generate",
  "n_scenes": 5,
  "frame_template": "1080x1920/image_default.html",
  "template_params": {
    "accent_color": "#3498db",
    "background": "https://example.com/custom-bg.jpg"
  },
  "title": "The Power of Reading"
}
```

**Response**:

```json
{
  "success": true,
  "message": "Success",
  "video_url": "http://localhost:8000/api/files/xxx/final.mp4",
  "duration": 45.5,
  "file_size": 12345678
}
```

### Sinh video — Bất đồng bộ

`POST /api/video/generate/async`

Sinh video bất đồng bộ, trả về task ID ngay lập tức. Phù hợp với video lớn.

**Response**:

```json
{
  "success": true,
  "message": "Task created successfully",
  "task_id": "abc123"
}
```

### Truy vấn trạng thái task

`GET /api/tasks/{task_id}`

**Response**:

```json
{
  "task_id": "abc123",
  "status": "completed",
  "result": {
    "video_url": "http://localhost:8000/api/files/xxx/final.mp4",
    "duration": 45.5,
    "file_size": 12345678
  }
}
```

---

## Tham số request

| Tham số | Kiểu | Bắt buộc | Mô tả |
|-----------|------|----------|-------------|
| `text` | string | Có | Chủ đề hoặc kịch bản hoàn chỉnh |
| `mode` | string | Không | `"generate"` (AI sinh) hoặc `"fixed"` (dùng nguyên text) |
| `n_scenes` | int | Không | Số cảnh (1–20), chỉ dùng ở chế độ generate |
| `title` | string | Không | Tiêu đề video (tự tạo nếu không cung cấp) |
| `frame_template` | string | Không | Đường dẫn template, ví dụ `1080x1920/image_default.html` |
| `template_params` | object | Không | Tham số tuỳ chỉnh template (màu, nền, …) |
| `media_workflow` | string | Không | Workflow media (sinh ảnh hoặc video) |
| `tts_workflow` | string | Không | Workflow TTS |
| `ref_audio` | string | Không | Đường dẫn audio tham chiếu cho voice cloning |
| `prompt_prefix` | string | Không | Tiền tố phong cách ảnh |
| `bgm_path` | string | Không | Đường dẫn file BGM |
| `bgm_volume` | float | Không | Âm lượng BGM (0.0–1.0, mặc định 0.3) |

---

## Thông tin thêm

Tài liệu API cũng có sẵn qua Swagger UI: `http://localhost:8000/docs`
