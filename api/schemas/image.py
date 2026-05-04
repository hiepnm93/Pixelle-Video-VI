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
Các schema cho API tạo ảnh
"""

from typing import Optional
from pydantic import BaseModel, Field


class ImageGenerateRequest(BaseModel):
    """Yêu cầu tạo ảnh"""
    prompt: str = Field(..., description="Prompt tạo ảnh")
    width: int = Field(1024, ge=512, le=2048, description="Chiều rộng ảnh")
    height: int = Field(1024, ge=512, le=2048, description="Chiều cao ảnh")
    workflow: Optional[str] = Field(None, description="Tên file workflow tuỳ chỉnh")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "A serene mountain landscape at sunset, photorealistic style",
                "width": 1024,
                "height": 1024
            }
        }


class ImageGenerateResponse(BaseModel):
    """Phản hồi tạo ảnh"""
    success: bool = True
    message: str = "Success"
    image_path: str = Field(..., description="Đường dẫn tới ảnh đã tạo")

