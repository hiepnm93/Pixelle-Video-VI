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
Base Pipeline cho việc tạo video

Tất cả pipeline tuỳ chỉnh nên kế thừa từ BasePipeline.
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable

from loguru import logger

from pixelle_video.models.progress import ProgressEvent
from pixelle_video.models.storyboard import VideoGenerationResult


class BasePipeline(ABC):
    """
    Pipeline cơ sở cho việc tạo video

    Tất cả pipeline tuỳ chỉnh nên kế thừa từ class này và implement __call__.

    Nguyên tắc thiết kế:
    - Mỗi pipeline đại diện cho một workflow tạo video hoàn chỉnh
    - Các pipeline độc lập và có thể có logic hoàn toàn khác nhau
    - Pipeline có quyền truy cập tới tất cả service core qua self.core
    - Pipeline nên báo cáo tiến độ qua progress_callback

    Ví dụ:
        >>> class MyPipeline(BasePipeline):
        ...     async def __call__(self, text: str, **kwargs):
        ...         # Bước 1: Sinh nội dung
        ...         narrations = await some_logic(text)
        ...
        ...         # Bước 2: Xử lý các frame
        ...         for narration in narrations:
        ...             audio = await self.core.tts(narration)
        ...             # ...
        ...
        ...         return VideoGenerationResult(...)
    """
    
    def __init__(self, pixelle_video_core):
        """
        Khởi tạo pipeline với các service core

        Args:
            pixelle_video_core: Instance PixelleVideoCore (cho phép truy cập tất cả service)
        """
        self.core = pixelle_video_core

        # Truy cập nhanh tới các service (tiện lợi)
        self.llm = pixelle_video_core.llm
        self.tts = pixelle_video_core.tts
        self.media = pixelle_video_core.media
        self.video = pixelle_video_core.video

        # Alias để tương thích ngược
        self.image = pixelle_video_core.media
    
    @abstractmethod
    async def __call__(
        self,
        text: str,
        progress_callback: Optional[Callable[[ProgressEvent], None]] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """
        Thực thi pipeline

        Args:
            text: Văn bản đầu vào (ý nghĩa tuỳ theo từng pipeline)
            progress_callback: Callback tuỳ chọn cho cập nhật tiến độ (nhận ProgressEvent)
            **kwargs: Tham số riêng của pipeline

        Returns:
            VideoGenerationResult kèm đường dẫn video và metadata

        Raises:
            Exception: Các ngoại lệ riêng của pipeline
        """
        pass

    def _report_progress(
        self,
        callback: Optional[Callable[[ProgressEvent], None]],
        event_type: str,
        progress: float,
        **kwargs
    ):
        """
        Báo cáo tiến độ qua callback

        Args:
            callback: Hàm callback tiến độ
            event_type: Loại sự kiện tiến độ
            progress: Giá trị tiến độ (0.0-1.0)
            **kwargs: Các tham số bổ sung riêng cho sự kiện (frame_current, frame_total, v.v.)
        """
        if callback:
            event = ProgressEvent(event_type=event_type, progress=progress, **kwargs)
            callback(event)
            logger.debug(f"Tiến độ: {progress*100:.0f}% - {event_type}")
        else:
            logger.debug(f"Tiến độ: {progress*100:.0f}% - {event_type}")

