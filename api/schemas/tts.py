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
Các schema cho API TTS
"""

from typing import Optional
from pydantic import BaseModel, Field


class TTSSynthesizeRequest(BaseModel):
    """Yêu cầu tổng hợp TTS"""
    text: str = Field(..., description="Văn bản cần tổng hợp")
    workflow: Optional[str] = Field(
        None,
        description="Khoá workflow TTS (ví dụ: 'runninghub/tts_edge.json' hoặc 'selfhost/tts_edge.json'). Nếu không chỉ định, dùng workflow mặc định từ config."
    )
    ref_audio: Optional[str] = Field(
        None,
        description="Đường dẫn audio tham chiếu để nhân bản giọng (tuỳ chọn). Có thể là đường dẫn file cục bộ hoặc URL."
    )
    voice_id: Optional[str] = Field(
        None,
        description="ID giọng (đã lỗi thời, hãy dùng workflow thay thế)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "text": "Hello, welcome to Pixelle-Video!",
                "workflow": "runninghub/tts_edge.json",
                "ref_audio": None
            }
        }


class TTSSynthesizeResponse(BaseModel):
    """Phản hồi tổng hợp TTS"""
    success: bool = True
    message: str = "Success"
    audio_path: str = Field(..., description="Đường dẫn tới file audio đã tạo")
    duration: float = Field(..., description="Thời lượng audio tính bằng giây")

