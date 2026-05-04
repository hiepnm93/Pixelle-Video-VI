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
Các schema cho API tạo nội dung
"""

from typing import List, Optional
from pydantic import BaseModel, Field


# ============================================================================
# Tạo lời thoại
# ============================================================================

class NarrationGenerateRequest(BaseModel):
    """Yêu cầu tạo lời thoại"""
    text: str = Field(..., description="Văn bản nguồn để tạo lời thoại")
    n_scenes: int = Field(5, ge=1, le=20, description="Số lượng cảnh")
    min_words: int = Field(5, ge=1, le=100, description="Số từ tối thiểu mỗi lời thoại")
    max_words: int = Field(20, ge=1, le=200, description="Số từ tối đa mỗi lời thoại")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Atomic Habits is about making small changes that lead to remarkable results.",
                "n_scenes": 5,
                "min_words": 5,
                "max_words": 20
            }
        }


class NarrationGenerateResponse(BaseModel):
    """Phản hồi tạo lời thoại"""
    success: bool = True
    message: str = "Success"
    narrations: List[str] = Field(..., description="Các lời thoại đã tạo")


# ============================================================================
# Tạo prompt ảnh
# ============================================================================

class ImagePromptGenerateRequest(BaseModel):
    """Yêu cầu tạo prompt ảnh"""
    narrations: List[str] = Field(..., description="Danh sách lời thoại")
    min_words: int = Field(30, ge=10, le=100, description="Số từ tối thiểu mỗi prompt")
    max_words: int = Field(60, ge=10, le=200, description="Số từ tối đa mỗi prompt")

    class Config:
        json_schema_extra = {
            "example": {
                "narrations": [
                    "Small habits compound over time",
                    "Focus on systems, not goals"
                ],
                "min_words": 30,
                "max_words": 60
            }
        }


class ImagePromptGenerateResponse(BaseModel):
    """Phản hồi tạo prompt ảnh"""
    success: bool = True
    message: str = "Success"
    image_prompts: List[str] = Field(..., description="Các prompt ảnh đã tạo")


# ============================================================================
# Tạo tiêu đề
# ============================================================================

class TitleGenerateRequest(BaseModel):
    """Yêu cầu tạo tiêu đề"""
    text: str = Field(..., description="Văn bản nguồn")
    style: Optional[str] = Field(None, description="Phong cách tiêu đề (ví dụ: 'engaging', 'formal')")

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Atomic Habits is about making small changes that lead to remarkable results.",
                "style": "engaging"
            }
        }


class TitleGenerateResponse(BaseModel):
    """Phản hồi tạo tiêu đề"""
    success: bool = True
    message: str = "Success"
    title: str = Field(..., description="Tiêu đề đã tạo")
