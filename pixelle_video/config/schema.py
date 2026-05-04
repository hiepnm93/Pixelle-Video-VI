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
Schema cấu hình với các model Pydantic

Nguồn duy nhất cho tất cả giá trị mặc định và xác thực cấu hình.
"""
from typing import Optional
from pydantic import BaseModel, Field


class LLMConfig(BaseModel):
    """Cấu hình LLM"""
    api_key: str = Field(default="", description="LLM API Key")
    base_url: str = Field(default="", description="LLM API Base URL")
    model: str = Field(default="", description="Tên model LLM")


class TTSLocalConfig(BaseModel):
    """Cấu hình TTS local (Edge TTS)"""
    voice: str = Field(default="zh-CN-YunjianNeural", description="ID giọng nói Edge TTS")
    speed: float = Field(default=1.2, ge=0.5, le=2.0, description="Hệ số tốc độ đọc (0.5-2.0)")


class TTSComfyUIConfig(BaseModel):
    """Cấu hình ComfyUI TTS"""
    default_workflow: Optional[str] = Field(default=None, description="Workflow TTS mặc định (tuỳ chọn)")


class TTSSubConfig(BaseModel):
    """Cấu hình riêng cho TTS (nằm dưới comfyui.tts)"""
    inference_mode: str = Field(default="local", description="Chế độ inference TTS: 'local' hoặc 'comfyui'")
    local: TTSLocalConfig = Field(default_factory=TTSLocalConfig, description="Cấu hình TTS local (Edge TTS)")
    comfyui: TTSComfyUIConfig = Field(default_factory=TTSComfyUIConfig, description="Cấu hình ComfyUI TTS")

    # Tương thích ngược: giữ default_workflow ở cấp cao nhất
    @property
    def default_workflow(self) -> Optional[str]:
        """Lấy workflow mặc định (giữ tương thích ngược)"""
        return self.comfyui.default_workflow


class ImageSubConfig(BaseModel):
    """Cấu hình riêng cho Image (nằm dưới comfyui.image)"""
    default_workflow: Optional[str] = Field(default=None, description="Workflow tạo ảnh mặc định (tuỳ chọn)")
    prompt_prefix: str = Field(
        default="Minimalist black-and-white matchstick figure style illustration, clean lines, simple sketch style",
        description="Tiền tố prompt cho mọi lệnh tạo ảnh"
    )


class VideoSubConfig(BaseModel):
    """Cấu hình riêng cho Video (nằm dưới comfyui.video)"""
    default_workflow: Optional[str] = Field(default=None, description="Workflow tạo video mặc định (tuỳ chọn)")
    prompt_prefix: str = Field(
        default="Minimalist black-and-white matchstick figure style illustration, clean lines, simple sketch style",
        description="Tiền tố prompt cho mọi lệnh tạo video"
    )


class ComfyUIConfig(BaseModel):
    """Cấu hình ComfyUI (bao gồm thiết lập toàn cục và cấu hình riêng cho từng service)"""
    comfyui_url: str = Field(default="http://127.0.0.1:8188", description="URL của ComfyUI Server")
    comfyui_api_key: Optional[str] = Field(default=None, description="ComfyUI API Key (tuỳ chọn)")
    runninghub_api_key: Optional[str] = Field(default=None, description="RunningHub API Key (tuỳ chọn)")
    runninghub_concurrent_limit: int = Field(default=1, ge=1, le=10, description="Giới hạn số tác vụ chạy song song trên RunningHub (1-10)")
    runninghub_instance_type: Optional[str] = Field(default=None, description="Kiểu instance RunningHub (tuỳ chọn, đặt 'plus' để dùng VRAM 48GB)")
    tts: TTSSubConfig = Field(default_factory=TTSSubConfig, description="Cấu hình riêng cho TTS")
    image: ImageSubConfig = Field(default_factory=ImageSubConfig, description="Cấu hình riêng cho Image")
    video: VideoSubConfig = Field(default_factory=VideoSubConfig, description="Cấu hình riêng cho Video")


class TemplateConfig(BaseModel):
    """Cấu hình Template"""
    default_template: str = Field(
        default="1080x1920/default.html",
        description="Đường dẫn template frame mặc định"
    )


class PixelleVideoConfig(BaseModel):
    """Cấu hình chính của Pixelle-Video"""
    project_name: str = Field(default="Pixelle-Video", description="Tên project")
    llm: LLMConfig = Field(default_factory=LLMConfig)
    comfyui: ComfyUIConfig = Field(default_factory=ComfyUIConfig)
    template: TemplateConfig = Field(default_factory=TemplateConfig)

    def is_llm_configured(self) -> bool:
        """Kiểm tra LLM đã được cấu hình đầy đủ chưa"""
        return bool(
            self.llm.api_key and self.llm.api_key.strip() and
            self.llm.base_url and self.llm.base_url.strip() and
            self.llm.model and self.llm.model.strip()
        )

    def validate_required(self) -> bool:
        """Xác thực các cấu hình bắt buộc"""
        return self.is_llm_configured()

    def to_dict(self) -> dict:
        """Chuyển sang dictionary (giữ tương thích ngược)"""
        return self.model_dump()

