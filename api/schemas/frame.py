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
Các schema cho API render frame/template
"""

from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field


class FrameRenderRequest(BaseModel):
    """Yêu cầu render frame"""
    template: str = Field(
        ...,
        description="Khoá template (ví dụ: '1080x1920/default.html'). Cũng có thể chỉ là tên file (ví dụ: 'default.html') để dùng kích thước mặc định."
    )
    title: Optional[str] = Field(None, description="Tiêu đề frame (tuỳ chọn)")
    text: str = Field(..., description="Nội dung văn bản của frame")
    image: Optional[str] = Field(None, description="Đường dẫn ảnh hoặc URL (tuỳ chọn)")

    class Config:
        json_schema_extra = {
            "example": {
                "template": "1080x1920/default.html",
                "title": "Sample Title",
                "text": "This is a sample text for the frame.",
                "image": "resources/example.png"
            }
        }


class FrameRenderResponse(BaseModel):
    """Phản hồi render frame"""
    success: bool = True
    message: str = "Success"
    frame_path: str = Field(..., description="Đường dẫn tới ảnh frame đã tạo")
    width: int = Field(..., description="Chiều rộng frame tính bằng pixel")
    height: int = Field(..., description="Chiều cao frame tính bằng pixel")


class TemplateParamConfig(BaseModel):
    """Cấu hình của một tham số template"""
    type: str = Field(..., description="Kiểu tham số: 'text', 'number', 'color', 'bool'")
    default: Any = Field(..., description="Giá trị mặc định")
    label: str = Field(..., description="Nhãn hiển thị của tham số")


class TemplateParamsResponse(BaseModel):
    """Phản hồi tham số template"""
    success: bool = True
    message: str = "Success"
    template: str = Field(..., description="Đường dẫn template")
    media_width: int = Field(..., description="Chiều rộng media từ thẻ meta của template")
    media_height: int = Field(..., description="Chiều cao media từ thẻ meta của template")
    params: Dict[str, TemplateParamConfig] = Field(
        default_factory=dict,
        description="Tham số tuỳ chỉnh được định nghĩa trong template. Khoá là tên tham số, giá trị là config."
    )
