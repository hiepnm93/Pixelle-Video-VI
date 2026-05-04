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
Các model kết quả tạo media
"""

from typing import Literal, Optional
from pydantic import BaseModel, Field


class MediaResult(BaseModel):
    """
    Kết quả tạo media từ việc thực thi workflow

    Hỗ trợ cả output ảnh và video từ các workflow của ComfyUI.
    media_type cho biết loại media nào đã được tạo.

    Thuộc tính:
        media_type: Loại media được tạo ("image" hoặc "video")
        url: URL hoặc đường dẫn tới media được tạo
        duration: Độ dài tính bằng giây (chỉ áp dụng cho video, None với ảnh)

    Ví dụ:
        # Kết quả ảnh
        MediaResult(media_type="image", url="http://example.com/image.png")

        # Kết quả video
        MediaResult(media_type="video", url="http://example.com/video.mp4", duration=5.2)
    """

    media_type: Literal["image", "video"] = Field(
        description="Loại media được tạo"
    )
    url: str = Field(
        description="URL hoặc đường dẫn tới file media được tạo"
    )
    duration: Optional[float] = Field(
        None,
        description="Độ dài tính bằng giây (chỉ áp dụng cho video)"
    )

    @property
    def is_image(self) -> bool:
        """Kiểm tra đây có phải là kết quả ảnh không"""
        return self.media_type == "image"

    @property
    def is_video(self) -> bool:
        """Kiểm tra đây có phải là kết quả video không"""
        return self.media_type == "video"

