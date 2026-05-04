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
Pixelle-Video Core - Lớp Service

Cung cấp truy cập thống nhất tới tất cả tính năng (LLM, TTS, Image, v.v.)
"""

import hashlib
import json
from typing import Optional

from loguru import logger
from comfykit import ComfyKit

from pixelle_video.config import config_manager
from pixelle_video.services.llm_service import LLMService
from pixelle_video.services.tts_service import TTSService
from pixelle_video.services.media import MediaService
from pixelle_video.services.image_analysis import ImageAnalysisService
from pixelle_video.services.video_analysis import VideoAnalysisService
from pixelle_video.services.video import VideoService
from pixelle_video.services.frame_processor import FrameProcessor
from pixelle_video.services.persistence import PersistenceService
from pixelle_video.services.history_manager import HistoryManager
from pixelle_video.pipelines.standard import StandardPipeline
from pixelle_video.pipelines.custom import CustomPipeline
from pixelle_video.pipelines.asset_based import AssetBasedPipeline


class PixelleVideoCore:
    """
    Pixelle-Video Core - Lớp Service

    Cung cấp truy cập thống nhất tới tất cả tính năng.

    Cách dùng:
        from pixelle_video import pixelle_video

        # Khởi tạo
        await pixelle_video.initialize()

        # Dùng tính năng trực tiếp
        answer = await pixelle_video.llm("Giải thích về thói quen nguyên tử")
        audio = await pixelle_video.tts("Xin chào thế giới")
        media = await pixelle_video.media(prompt="một con mèo")

        # Kiểm tra các tính năng đang hoạt động
        print(f"Đang dùng LLM: {pixelle_video.llm.active}")
        print(f"TTS có sẵn: {pixelle_video.tts.available}")

    Kiến trúc (đơn giản hoá):
        PixelleVideoCore (lớp này)
          ├── config (cấu hình)
          ├── llm (LLM service - dùng trực tiếp OpenAI SDK)
          ├── tts (TTS service - workflow của ComfyKit)
          ├── media (Media service - workflow của ComfyKit, hỗ trợ ảnh & video)
          └── pipelines (các pipeline tạo video)
              ├── standard (workflow tiêu chuẩn)
              ├── custom (mẫu workflow tuỳ chỉnh)
              └── ... (có thể mở rộng)
    """

    def __init__(self, config_path: str = "config.yaml"):
        """
        Khởi tạo Pixelle-Video Core

        Args:
            config_path: Đường dẫn tới file cấu hình
        """
        # Dùng singleton config manager toàn cục
        self.config = config_manager.config.to_dict()
        self._initialized = False

        # ComfyKit khởi tạo lười (tạo khi sử dụng lần đầu, tạo lại khi cấu hình thay đổi)
        self._comfykit: Optional[ComfyKit] = None
        self._comfykit_config_hash: Optional[str] = None

        # Các service core (được khởi tạo trong initialize())
        self.llm: Optional[LLMService] = None
        self.tts: Optional[TTSService] = None
        self.media: Optional[MediaService] = None
        self.video: Optional[VideoService] = None
        self.frame_processor: Optional[FrameProcessor] = None
        self.persistence: Optional[PersistenceService] = None
        self.history: Optional[HistoryManager] = None

        # Các pipeline tạo video (dictionary pipeline_name -> pipeline_instance)
        self.pipelines = {}

        # Pipeline mặc định callable (giữ tương thích ngược)
        self.generate_video = None

    def _get_comfykit_config(self) -> dict:
        """
        Lấy cấu hình ComfyKit hiện tại từ config_manager

        Returns:
            Dict cấu hình ComfyKit
        """
        # Reload cấu hình từ config_manager toàn cục (để hỗ trợ hot reload)
        self.config = config_manager.config.to_dict()

        comfyui_config = self.config.get("comfyui", {})
        kit_config = {}

        if comfyui_config.get("comfyui_url"):
            kit_config["comfyui_url"] = comfyui_config["comfyui_url"]
        if comfyui_config.get("comfyui_api_key"):
            kit_config["api_key"] = comfyui_config["comfyui_api_key"]
        if comfyui_config.get("runninghub_api_key"):
            kit_config["runninghub_api_key"] = comfyui_config["runninghub_api_key"]
        # Chỉ truyền instance_type nếu có giá trị không rỗng
        instance_type = comfyui_config.get("runninghub_instance_type")
        if instance_type and instance_type.strip():
            kit_config["runninghub_instance_type"] = instance_type

        return kit_config

    def _compute_comfykit_config_hash(self, config: dict) -> str:
        """
        Tính hash của cấu hình ComfyKit để phát hiện thay đổi

        Args:
            config: Dict cấu hình ComfyKit

        Returns:
            MD5 hash của cấu hình
        """
        # Sắp xếp keys để hash nhất quán
        config_str = json.dumps(config, sort_keys=True)
        return hashlib.md5(config_str.encode()).hexdigest()

    async def _get_or_create_comfykit(self) -> ComfyKit:
        """
        Lấy hoặc tạo instance ComfyKit (khởi tạo lười kèm phát hiện thay đổi cấu hình)

        Phương thức này:
        1. Tạo ComfyKit khi dùng lần đầu (lazy init)
        2. Phát hiện thay đổi cấu hình và tạo lại instance nếu cần
        3. Đảm bảo dọn dẹp instance cũ đúng cách

        Returns:
            Instance ComfyKit
        """
        current_config = self._get_comfykit_config()
        current_hash = self._compute_comfykit_config_hash(current_config)

        # Kiểm tra xem có cần tạo hoặc tạo lại ComfyKit không
        if self._comfykit is None or self._comfykit_config_hash != current_hash:
            # Đóng instance cũ nếu tồn tại
            if self._comfykit is not None:
                logger.info("🔄 Cấu hình ComfyUI đã thay đổi, đang tạo lại instance ComfyKit...")
                try:
                    await self._comfykit.close()
                except Exception as e:
                    logger.warning(f"Không thể đóng instance ComfyKit cũ: {e}")
                self._comfykit = None

            # Tạo instance mới với cấu hình hiện tại
            logger.info("✨ Đang tạo instance ComfyKit...")
            logger.debug(f"Cấu hình ComfyKit: {current_config}")
            self._comfykit = ComfyKit(**current_config)
            self._comfykit_config_hash = current_hash
            logger.info("✅ Đã tạo instance ComfyKit")

        return self._comfykit

    async def initialize(self):
        """
        Khởi tạo các tính năng core

        Khởi tạo tất cả service và phải được gọi trước khi sử dụng bất kỳ tính năng nào.
        Lưu ý: ComfyKit KHÔNG được khởi tạo ở đây - nó sẽ được khởi tạo lười khi dùng lần đầu.

        Ví dụ:
            await pixelle_video.initialize()
        """
        if self._initialized:
            logger.warning("Pixelle-Video đã được khởi tạo rồi")
            return

        logger.info("🚀 Đang khởi tạo Pixelle-Video...")

        # 1. Khởi tạo các service core (ComfyKit sẽ được lazy-load sau)
        # Khởi tạo các service
        self.llm = LLMService(self.config)
        self.tts = TTSService(self.config, core=self)
        self.media = MediaService(self.config, core=self)
        self.image = self.media  # Alias để tương thích ngược
        self.image_analysis = ImageAnalysisService(self.config, core=self)
        self.video_analysis = VideoAnalysisService(self.config, core=self)
        self.video = VideoService()
        self.frame_processor = FrameProcessor(self)
        self.persistence = PersistenceService(output_dir="output")
        self.history = HistoryManager(self.persistence)

        # 2. Đăng ký các pipeline tạo video
        self.pipelines = {
            "standard": StandardPipeline(self),
            "custom": CustomPipeline(self),
            "asset_based": AssetBasedPipeline(self),
        }
        logger.info(f"📹 Đã đăng ký pipeline: {', '.join(self.pipelines.keys())}")

        # 3. Đặt callable pipeline mặc định (giữ tương thích ngược)
        self.generate_video = self._create_generate_video_wrapper()

        self._initialized = True
        logger.info("✅ Pixelle-Video đã khởi tạo thành công\n")

    async def cleanup(self):
        """
        Dọn dẹp tài nguyên (đóng phiên ComfyKit)

        Ví dụ:
            await pixelle_video.cleanup()
        """
        if self._comfykit:
            logger.info("🧹 Đang đóng phiên ComfyKit...")
            try:
                await self._comfykit.close()
                logger.info("✅ Đã đóng phiên ComfyKit")
            except Exception as e:
                logger.error(f"Không thể đóng ComfyKit: {e}")
            finally:
                self._comfykit = None
                self._comfykit_config_hash = None

    async def __aenter__(self):
        """Async context manager - vào"""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager - thoát"""
        await self.cleanup()

    def _create_generate_video_wrapper(self):
        """
        Tạo hàm wrapper cho generate_video hỗ trợ chọn pipeline

        Giữ tương thích ngược đồng thời thêm hỗ trợ pipeline.
        """
        async def generate_video_wrapper(
            text: str,
            pipeline: str = "standard",
            **kwargs
        ):
            """
            Tạo video bằng pipeline được chỉ định

            Args:
                text: Văn bản đầu vào
                pipeline: Tên pipeline ("standard", "book_summary", v.v.)
                **kwargs: Tham số riêng cho từng pipeline

            Returns:
                VideoGenerationResult

            Ví dụ:
                # Dùng pipeline tiêu chuẩn (mặc định)
                result = await pixelle_video.generate_video(
                    text="Cách nâng cao hiệu quả học tập",
                    n_scenes=5
                )

                # Dùng pipeline tuỳ chỉnh
                result = await pixelle_video.generate_video(
                    text=your_content,
                    pipeline="custom",
                    custom_param_example="custom_value"
                )
            """
            if pipeline not in self.pipelines:
                available = ", ".join(self.pipelines.keys())
                raise ValueError(
                    f"Không tìm thấy pipeline: '{pipeline}'. "
                    f"Pipeline có sẵn: {available}"
                )

            pipeline_instance = self.pipelines[pipeline]
            return await pipeline_instance(text=text, **kwargs)

        return generate_video_wrapper

    @property
    def project_name(self) -> str:
        """Lấy tên project từ cấu hình"""
        return self.config.get("project_name", "Pixelle-Video")

    def __repr__(self) -> str:
        """Biểu diễn dạng chuỗi"""
        status = "đã khởi tạo" if self._initialized else "chưa khởi tạo"
        pipelines = f"pipelines={list(self.pipelines.keys())}" if self._initialized else ""
        return f"<PixelleVideoCore project={self.project_name!r} status={status} {pipelines}>"


# Instance toàn cục
pixelle_video = PixelleVideoCore()
