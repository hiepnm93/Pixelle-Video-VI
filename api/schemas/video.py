# Copyright (C) 2025 AIDC-AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#     http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Các schema cho API tạo video
"""

from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field


class VideoGenerateRequest(BaseModel):
    """Yêu cầu tạo video"""

    # === Đầu vào ===
    text: str = Field(..., description="Văn bản nguồn để tạo video")

    # === Chế độ xử lý ===
    mode: Literal["generate", "fixed"] = Field(
        "generate",
        description="Chế độ xử lý: 'generate' (AI tạo lời thoại) hoặc 'fixed' (dùng văn bản nguyên trạng)"
    )

    # === Tiêu đề tuỳ chọn ===
    title: Optional[str] = Field(None, description="Tiêu đề video (tự động tạo nếu không cung cấp)")

    # === Cấu hình cơ bản ===
    n_scenes: Optional[int] = Field(5, ge=1, le=20, description="Số lượng cảnh (chỉ dùng ở chế độ 'generate', bỏ qua ở chế độ 'fixed')")

    # === Tham số TTS ===
    tts_workflow: Optional[str] = Field(
        None,
        description="Khoá workflow TTS (ví dụ: 'runninghub/tts_edge.json'). Nếu không chỉ định, dùng workflow mặc định từ config."
    )
    ref_audio: Optional[str] = Field(
        None,
        description="Đường dẫn audio tham chiếu để nhân bản giọng (tuỳ chọn)"
    )
    voice_id: Optional[str] = Field(
        None,
        description="(Đã lỗi thời) ID giọng TTS để tương thích phiên bản cũ"
    )

    # === Tham số LLM ===
    min_narration_words: int = Field(5, ge=1, le=100, description="Số từ tối thiểu của lời thoại")
    max_narration_words: int = Field(20, ge=1, le=200, description="Số từ tối đa của lời thoại")
    min_image_prompt_words: int = Field(30, ge=10, le=100, description="Số từ tối thiểu của prompt ảnh")
    max_image_prompt_words: int = Field(60, ge=10, le=200, description="Số từ tối đa của prompt ảnh")

    # === Tham số Media ===
    # Lưu ý: media_width và media_height được tự động xác định từ thẻ meta của template
    media_workflow: Optional[str] = Field(None, description="Workflow media tuỳ chỉnh (ảnh hoặc video)")

    # === Tham số Video ===
    video_fps: int = Field(30, ge=15, le=60, description="FPS của video")

    # === Frame Template (xác định kích thước video) ===
    frame_template: Optional[str] = Field(
        None,
        description="Đường dẫn template HTML kèm kích thước (ví dụ: '1080x1920/default.html'). Kích thước video tự động xác định từ template."
    )

    # === Tham số tuỳ chỉnh của Template ===
    template_params: Optional[Dict[str, Any]] = Field(
        None,
        description="Tham số template tuỳ chỉnh (ví dụ: {'accent_color': '#ff0000', 'background': 'url'}). "
                    "Tham số có sẵn phụ thuộc vào template. Dùng GET /api/templates/{template_path}/params để khám phá."
    )

    # === Phong cách ảnh ===
    prompt_prefix: Optional[str] = Field(None, description="Tiền tố phong cách ảnh")

    # === BGM ===
    bgm_path: Optional[str] = Field(None, description="Đường dẫn nhạc nền")
    bgm_volume: float = Field(0.3, ge=0.0, le=1.0, description="Âm lượng BGM (0.0-1.0)")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Atomic Habits teaches us that small changes compound over time to produce remarkable results.",
                "mode": "generate",
                "n_scenes": 5,
                "frame_template": "1080x1920/image_default.html",
                "template_params": {
                    "accent_color": "#3498db",
                    "background": "https://example.com/custom-bg.jpg"
                },
                "title": "The Power of Atomic Habits"
            }
        }


class VideoGenerateResponse(BaseModel):
    """Phản hồi tạo video (đồng bộ)"""
    success: bool = True
    message: str = "Success"
    video_url: str = Field(..., description="URL để truy cập video đã tạo")
    duration: float = Field(..., description="Thời lượng video tính bằng giây")
    file_size: int = Field(..., description="Kích thước file tính bằng byte")


class VideoGenerateAsyncResponse(BaseModel):
    """Phản hồi tạo video bất đồng bộ"""
    success: bool = True
    message: str = "Task created successfully"
    task_id: str = Field(..., description="ID task để theo dõi tiến trình")
