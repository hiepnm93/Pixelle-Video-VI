# Schema cấu hình

Giải thích chi tiết file cấu hình `config.yaml`.

---

## Cấu trúc cấu hình

```yaml
llm:
  api_key: "your-api-key"
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
  model: "qwen-plus"

comfyui:
  comfyui_url: "http://127.0.0.1:8188"
  comfyui_api_key: ""  # ComfyUI API key (tuỳ chọn)
  runninghub_api_key: ""
  runninghub_concurrent_limit: 1  # Giới hạn concurrency (1-10)
  runninghub_instance_type: ""  # Loại instance (tuỳ chọn, đặt "plus" cho 48GB VRAM)
  
  image:
    default_workflow: "runninghub/image_flux.json"
    prompt_prefix: "Minimalist illustration style"
  
  video:
    default_workflow: "runninghub/video_wan2.1_fusionx.json"
    prompt_prefix: "Minimalist illustration style"
  
  tts:
    default_workflow: "selfhost/tts_edge.json"

template:
  default_template: "1080x1920/image_default.html"
```

---

## Cấu hình LLM

- `api_key`: API key
- `base_url`: Địa chỉ dịch vụ API (hỗ trợ mọi endpoint tương thích OpenAI)
- `model`: Tên model

---

## Cấu hình ComfyUI

### Cấu hình cơ bản

- `comfyui_url`: Địa chỉ ComfyUI cục bộ (mặc định `http://127.0.0.1:8188`)
- `comfyui_api_key`: ComfyUI API key (tuỳ chọn, dành cho [Comfy Platform](https://platform.comfy.org/profile/api-keys))

### Cấu hình cloud RunningHub

- `runninghub_api_key`: API key của RunningHub (bắt buộc cho workflow cloud)
- `runninghub_concurrent_limit`: Giới hạn thực thi concurrency (1–10, mặc định 1 cho tài khoản thường)
- `runninghub_instance_type`: Loại instance (tuỳ chọn)
  - Trống hoặc không đặt: Dùng máy 24GB VRAM
  - `"plus"`: Dùng máy 48GB VRAM (phù hợp sinh video kích thước lớn)

### Cấu hình ảnh

- `default_workflow`: Workflow sinh ảnh mặc định
- `prompt_prefix`: Tiền tố prompt

### Cấu hình video

- `default_workflow`: Workflow sinh video mặc định
  - `runninghub/video_wan2.1_fusionx.json`: Workflow cloud (khuyến nghị, không cần thiết lập cục bộ)
  - `selfhost/video_wan2.1_fusionx.json`: Workflow cục bộ (cần ComfyUI cục bộ hỗ trợ)
- `prompt_prefix`: Tiền tố prompt video (điều khiển phong cách sinh video)

### Cấu hình TTS

- `default_workflow`: Workflow TTS mặc định

---

## Cấu hình Template

- `default_template`: Đường dẫn template khung hình mặc định (ví dụ `1080x1920/image_default.html`)

---

## Thông tin thêm

File cấu hình được tự động tạo khi chạy lần đầu.
