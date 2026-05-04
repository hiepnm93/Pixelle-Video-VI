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
Các schema cho API LLM
"""

from typing import Optional
from pydantic import BaseModel, Field


class LLMChatRequest(BaseModel):
    """Yêu cầu chat LLM"""
    prompt: str = Field(..., description="Prompt của người dùng")
    temperature: float = Field(0.7, ge=0.0, le=2.0, description="Temperature (0.0-2.0)")
    max_tokens: int = Field(2000, ge=1, le=32000, description="Số token tối đa")

    class Config:
        json_schema_extra = {
            "example": {
                "prompt": "Explain the concept of atomic habits in 3 sentences",
                "temperature": 0.7,
                "max_tokens": 2000
            }
        }


class LLMChatResponse(BaseModel):
    """Phản hồi chat LLM"""
    success: bool = True
    message: str = "Success"
    content: str = Field(..., description="Phản hồi đã tạo")
    tokens_used: Optional[int] = Field(None, description="Số token đã dùng (nếu có)")

