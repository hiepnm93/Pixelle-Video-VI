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
Service tạo Media - Triển khai dựa trên workflow ComfyUI

Hỗ trợ cả workflow tạo image và tạo video.
Tự động phát hiện loại output dựa trên ExecuteResult.
"""

from typing import Optional

from comfykit import ComfyKit
from loguru import logger

from pixelle_video.services.comfy_base_service import ComfyBaseService
from pixelle_video.models.media import MediaResult


class MediaService(ComfyBaseService):
    """
    Service tạo media - dựa trên workflow

    Sử dụng ComfyKit để chạy các workflow tạo image/video.
    Hỗ trợ cả tiền tố workflow image_ và video_.

    Cách dùng:
        # Dùng workflow mặc định (workflows/image_flux.json)
        media = await pixelle_video.media(prompt="a cat")
        if media.is_image:
            print(f"Đã tạo image: {media.url}")
        elif media.is_video:
            print(f"Đã tạo video: {media.url} ({media.duration}s)")

        # Dùng workflow cụ thể
        media = await pixelle_video.media(
            prompt="a cat",
            workflow="image_flux.json"
        )

        # Liệt kê các workflow có sẵn
        workflows = pixelle_video.media.list_workflows()
    """

    WORKFLOW_PREFIX = ""  # Sẽ được ghi đè bởi _scan_workflows
    DEFAULT_WORKFLOW = None  # Không có giá trị mặc định cứng, bắt buộc phải cấu hình
    WORKFLOWS_DIR = "workflows"

    def __init__(self, config: dict, core=None):
        """
        Khởi tạo media service

        Args:
            config: Dict cấu hình đầy đủ của ứng dụng
            core: Instance PixelleVideoCore (để truy cập ComfyKit dùng chung)
        """
        super().__init__(config, service_name="image", core=core)  # Giữ "image" để tương thích config
    
    def _scan_workflows(self):
        """
        Quét các workflow có tiền tố image_ và video_

        Ghi đè phương thức của lớp cha để hỗ trợ nhiều tiền tố
        """
        from pixelle_video.utils.os_util import list_resource_dirs, list_resource_files, get_resource_path
        from pathlib import Path

        workflows = []

        # Lấy tất cả thư mục nguồn workflow
        source_dirs = list_resource_dirs("workflows")

        if not source_dirs:
            logger.warning("Không tìm thấy thư mục nguồn workflow nào")
            return workflows

        # Quét từng thư mục nguồn để tìm file workflow
        for source_name in source_dirs:
            # Lấy tất cả file JSON cho nguồn này
            workflow_files = list_resource_files("workflows", source_name)

            # Lọc chỉ những file có tiền tố image_ hoặc video_
            matching_files = [
                f for f in workflow_files
                if (f.startswith("image_") or f.startswith("video_")) and f.endswith('.json')
            ]

            for filename in matching_files:
                try:
                    # Lấy đường dẫn file thực tế
                    file_path = Path(get_resource_path("workflows", source_name, filename))
                    workflow_info = self._parse_workflow_file(file_path, source_name)
                    workflows.append(workflow_info)
                    logger.debug(f"Đã tìm thấy workflow: {workflow_info['key']}")
                except Exception as e:
                    logger.error(f"Không parse được workflow {source_name}/{filename}: {e}")

        # Sắp xếp theo key (source/name)
        return sorted(workflows, key=lambda w: w["key"])
    
    async def __call__(
        self,
        prompt: str,
        workflow: Optional[str] = None,
        # Khai báo loại media (bắt buộc để xử lý đúng)
        media_type: str = "image",  # "image" hoặc "video"
        # Kết nối ComfyUI (tùy chọn ghi đè)
        comfyui_url: Optional[str] = None,
        runninghub_api_key: Optional[str] = None,
        # Tham số workflow phổ biến
        width: Optional[int] = None,
        height: Optional[int] = None,
        duration: Optional[float] = None,  # Thời lượng video tính bằng giây (dùng cho workflow video)
        negative_prompt: Optional[str] = None,
        steps: Optional[int] = None,
        seed: Optional[int] = None,
        cfg: Optional[float] = None,
        sampler: Optional[str] = None,
        **params
    ) -> MediaResult:
        """
        Tạo media (image hoặc video) bằng workflow

        Loại media phải được chỉ định rõ qua tham số media_type.
        Trả về đối tượng MediaResult chứa loại media và URL.

        Args:
            prompt: Prompt để tạo media
            workflow: Tên file workflow (mặc định: từ config hoặc "image_flux.json")
            media_type: Loại media cần tạo - "image" hoặc "video" (mặc định: "image")
            comfyui_url: URL của ComfyUI (tùy chọn, ghi đè config)
            runninghub_api_key: API Key của RunningHub (tùy chọn, ghi đè config)
            width: Chiều rộng media
            height: Chiều cao media
            duration: Thời lượng video mục tiêu tính bằng giây (chỉ dùng cho workflow video, thường lấy từ thời lượng audio TTS)
            negative_prompt: Negative prompt
            steps: Số bước sampling
            seed: Seed ngẫu nhiên
            cfg: Hệ số CFG
            sampler: Tên sampler
            **params: Tham số workflow bổ sung

        Returns:
            Đối tượng MediaResult với media_type ("image" hoặc "video") và url

        Ví dụ:
            # Đơn giản nhất: dùng workflow mặc định (workflows/image_flux.json)
            media = await pixelle_video.media(prompt="a beautiful cat")
            if media.is_image:
                print(f"Image: {media.url}")

            # Dùng workflow cụ thể
            media = await pixelle_video.media(
                prompt="a cat",
                workflow="image_flux.json"
            )

            # Workflow video
            media = await pixelle_video.media(
                prompt="a cat running",
                workflow="image_video.json"
            )
            if media.is_video:
                print(f"Video: {media.url}, thời lượng: {media.duration}s")

            # Với tham số bổ sung
            media = await pixelle_video.media(
                prompt="a cat",
                workflow="image_flux.json",
                width=1024,
                height=1024,
                steps=20,
                seed=42
            )

            # Với đường dẫn tuyệt đối
            media = await pixelle_video.media(
                prompt="a cat",
                workflow="/path/to/custom.json"
            )

            # Với máy chủ ComfyUI tùy chỉnh
            media = await pixelle_video.media(
                prompt="a cat",
                comfyui_url="http://192.168.1.100:8188"
            )
        """
        # 1. Resolve workflow (trả về thông tin có cấu trúc)
        workflow_info = self._resolve_workflow(workflow=workflow)

        # 2. Xây dựng tham số workflow (cấu hình ComfyKit hiện do core quản lý)
        workflow_params = {"prompt": prompt}

        # Thêm các tham số tùy chọn
        if width is not None:
            workflow_params["width"] = width
        if height is not None:
            workflow_params["height"] = height
        if duration is not None:
            workflow_params["duration"] = duration
            if media_type == "video":
                logger.info(f"📏 Thời lượng video mục tiêu: {duration:.2f}s (từ TTS audio)")
        if negative_prompt is not None:
            workflow_params["negative_prompt"] = negative_prompt
        if steps is not None:
            workflow_params["steps"] = steps
        if seed is not None:
            workflow_params["seed"] = seed
        if cfg is not None:
            workflow_params["cfg"] = cfg
        if sampler is not None:
            workflow_params["sampler"] = sampler

        # Thêm bất kỳ tham số bổ sung nào
        workflow_params.update(params)

        logger.debug(f"Tham số workflow: {workflow_params}")

        # 4. Chạy workflow bằng instance ComfyKit dùng chung từ core
        try:
            # Lấy instance ComfyKit dùng chung (khởi tạo lazy + hot-reload config)
            kit = await self.core._get_or_create_comfykit()

            # Xác định nội dung truyền vào ComfyKit dựa trên source
            if workflow_info["source"] == "runninghub" and "workflow_id" in workflow_info:
                # RunningHub: truyền workflow_id (ComfyKit sẽ dùng backend runninghub)
                workflow_input = workflow_info["workflow_id"]
                logger.info(f"Đang chạy workflow RunningHub: {workflow_input}")
            else:
                # Selfhost: truyền đường dẫn file (ComfyKit sẽ dùng ComfyUI cục bộ)
                workflow_input = workflow_info["path"]
                logger.info(f"Đang chạy workflow selfhost: {workflow_input}")

            result = await kit.execute(workflow_input, workflow_params)

            # 5. Xử lý kết quả dựa trên media_type đã chỉ định
            if result.status != "completed":
                error_msg = result.msg or "Lỗi không xác định"
                logger.error(f"Tạo media thất bại: {error_msg}")
                raise Exception(f"Tạo media thất bại: {error_msg}")

            # Trích xuất media theo loại đã chỉ định
            if media_type == "video":
                # Workflow video - lấy video từ kết quả
                if not result.videos:
                    logger.error("Không có video nào được tạo (workflow không trả về video)")
                    raise Exception("Không có video nào được tạo")

                video_url = result.videos[0]
                logger.info(f"✅ Đã tạo video: {video_url}")

                # Thử trích xuất thời lượng từ kết quả (nếu có)
                duration = None
                if hasattr(result, 'duration') and result.duration:
                    duration = result.duration

                return MediaResult(
                    media_type="video",
                    url=video_url,
                    duration=duration
                )
            else:  # image
                # Workflow image - lấy image từ kết quả
                if not result.images:
                    logger.error("Không có image nào được tạo (workflow không trả về image)")
                    raise Exception("Không có image nào được tạo")

                image_url = result.images[0]
                logger.info(f"✅ Đã tạo image: {image_url}")

                return MediaResult(
                    media_type="image",
                    url=image_url
                )

        except Exception as e:
            logger.error(f"Lỗi tạo media: {e}")
            raise
