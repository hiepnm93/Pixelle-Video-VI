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
Các model sự kiện tiến độ cho việc tạo video

Cung cấp các sự kiện tiến độ có cấu trúc để lớp UI tiêu thụ và dịch.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class ProgressEvent:
    """
    Sự kiện tiến độ có cấu trúc cho quá trình tạo video

    Thuộc tính:
        event_type: Loại sự kiện (ví dụ: "generating_narrations", "frame_step", "concatenating")
        progress: Giá trị tiến độ từ 0.0 đến 1.0
        frame_current: Số frame hiện tại (đếm từ 1, tuỳ chọn)
        frame_total: Tổng số frame (tuỳ chọn)
        step: Bước hiện tại trong frame (1-4, tuỳ chọn)
        action: Hành động đang thực hiện (ví dụ: "audio", "image", "compose", "video", tuỳ chọn)

    Ví dụ:
        # Sự kiện tiến độ đơn giản
        ProgressEvent(event_type="generating_narrations", progress=0.05)

        # Sự kiện bước frame
        ProgressEvent(
            event_type="frame_step",
            progress=0.23,
            frame_current=1,
            frame_total=5,
            step=1,
            action="audio"
        )
    """
    event_type: str
    progress: float

    # Các trường tuỳ chọn liên quan đến frame
    frame_current: Optional[int] = None
    frame_total: Optional[int] = None
    step: Optional[int] = None  # 1-4 cho các bước xử lý frame
    action: Optional[str] = None  # "audio", "image", "compose", "video"
    extra_info: Optional[str] = None  # Thông tin bổ sung (ví dụ: tiến độ batch)

    def __post_init__(self):
        """Xác thực giá trị progress"""
        if not 0.0 <= self.progress <= 1.0:
            raise ValueError(f"Progress phải nằm trong khoảng 0.0 đến 1.0, nhận được {self.progress}")

