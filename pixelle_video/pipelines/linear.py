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
Class cơ sở cho Linear Video Pipeline

Module này định nghĩa mẫu template method cho các workflow tạo video tuyến tính.
Giới thiệu `PipelineContext` để quản lý trạng thái và `LinearVideoPipeline` để
điều phối quy trình.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any, Callable
from loguru import logger

from pixelle_video.pipelines.base import BasePipeline
from pixelle_video.models.storyboard import (
    Storyboard,
    VideoGenerationResult,
    StoryboardConfig
)
from pixelle_video.models.progress import ProgressEvent


@dataclass
class PipelineContext:
    """
    Object context giữ trạng thái của một lần thực thi pipeline.

    Object này được truyền giữa các bước trong vòng đời LinearVideoPipeline.
    """
    # === Đầu vào ===
    input_text: str
    params: Dict[str, Any]
    progress_callback: Optional[Callable[[ProgressEvent], None]] = None

    # === Trạng thái Task ===
    task_id: Optional[str] = None
    task_dir: Optional[str] = None

    # === Nội dung ===
    title: Optional[str] = None
    narrations: List[str] = field(default_factory=list)

    # === Hình ảnh ===
    image_prompts: List[Optional[str]] = field(default_factory=list)

    # === Cấu hình & Storyboard ===
    config: Optional[StoryboardConfig] = None
    storyboard: Optional[Storyboard] = None

    # === Output ===
    final_video_path: Optional[str] = None
    result: Optional[VideoGenerationResult] = None


class LinearVideoPipeline(BasePipeline):
    """
    Class cơ sở cho các pipeline tạo video tuyến tính, dùng mẫu Template Method.

    Class này điều phối quá trình tạo video thành các bước vòng đời riêng biệt:
    1. setup_environment
    2. generate_content
    3. determine_title
    4. plan_visuals
    5. initialize_storyboard
    6. produce_assets
    7. post_production
    8. finalize

    Các subclass nên override các bước cụ thể để tuỳ chỉnh hành vi đồng thời giữ
    cấu trúc workflow tổng thể.
    """

    async def __call__(
        self,
        text: str,
        progress_callback: Optional[Callable[[ProgressEvent], None]] = None,
        **kwargs
    ) -> VideoGenerationResult:
        """
        Thực thi pipeline bằng template method.
        """
        # 1. Khởi tạo context
        ctx = PipelineContext(
            input_text=text,
            params=kwargs,
            progress_callback=progress_callback
        )

        try:
            # === Giai đoạn 1: Chuẩn bị ===
            await self.setup_environment(ctx)

            # === Giai đoạn 2: Tạo nội dung ===
            await self.generate_content(ctx)
            await self.determine_title(ctx)

            # === Giai đoạn 3: Lập kế hoạch hình ảnh ===
            await self.plan_visuals(ctx)
            await self.initialize_storyboard(ctx)

            # === Giai đoạn 4: Sản xuất tài nguyên ===
            await self.produce_assets(ctx)

            # === Giai đoạn 5: Hậu kỳ ===
            await self.post_production(ctx)

            # === Giai đoạn 6: Hoàn thiện ===
            return await self.finalize(ctx)

        except Exception as e:
            await self.handle_exception(ctx, e)
            raise

    # ==================== Các method vòng đời ====================

    async def setup_environment(self, ctx: PipelineContext):
        """Bước 1: Setup thư mục task và môi trường."""
        pass

    async def generate_content(self, ctx: PipelineContext):
        """Bước 2: Sinh hoặc xử lý kịch bản/thuyết minh."""
        pass

    async def determine_title(self, ctx: PipelineContext):
        """Bước 3: Xác định hoặc sinh tiêu đề video."""
        pass

    async def plan_visuals(self, ctx: PipelineContext):
        """Bước 4: Sinh prompt ảnh hoặc mô tả hình ảnh."""
        pass

    async def initialize_storyboard(self, ctx: PipelineContext):
        """Bước 5: Tạo object Storyboard và các frame."""
        pass

    async def produce_assets(self, ctx: PipelineContext):
        """Bước 6: Sinh audio, ảnh và render các frame (Xử lý cốt lõi)."""
        pass

    async def post_production(self, ctx: PipelineContext):
        """Bước 7: Ghép video và thêm BGM."""
        pass

    async def finalize(self, ctx: PipelineContext) -> VideoGenerationResult:
        """Bước 8: Tạo object kết quả và lưu metadata."""
        raise NotImplementedError("finalize phải được triển khai bởi subclass")

    async def handle_exception(self, ctx: PipelineContext, error: Exception):
        """Xử lý ngoại lệ trong khi thực thi pipeline."""
        logger.error(f"Thực thi pipeline thất bại: {error}")
