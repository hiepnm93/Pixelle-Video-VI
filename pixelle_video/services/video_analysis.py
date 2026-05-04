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
Service phân tích Video - Triển khai dựa trên workflow ComfyUI

Sử dụng các workflow ComfyUI để phân tích nội dung video và sinh mô tả.
"""

from typing import Optional, Literal
from pathlib import Path

from comfykit import ComfyKit
from loguru import logger

from pixelle_video.services.comfy_base_service import ComfyBaseService


class VideoAnalysisService(ComfyBaseService):
    """
    Service phân tích video - dựa trên workflow

    Sử dụng ComfyKit để chạy các workflow hiểu nội dung video.
    Trả về mô tả chi tiết bằng văn bản về nội dung video.

    Quy ước: workflow theo mẫu {source}/analyse_video.json
    - runninghub/analyse_video.json (mặc định, dùng cloud)
    - selfhost/analyse_video.json (ComfyUI cục bộ, tương lai)

    Cách dùng:
        # Dùng mặc định (runninghub cloud)
        description = await pixelle_video.video_analysis("path/to/video.mp4")

        # Dùng ComfyUI cục bộ (tương lai)
        description = await pixelle_video.video_analysis(
            "path/to/video.mp4",
            source="selfhost"
        )

        # Liệt kê các workflow có sẵn
        workflows = pixelle_video.video_analysis.list_workflows()
    """

    WORKFLOW_PREFIX = "analyse_video"
    WORKFLOWS_DIR = "workflows"

    def __init__(self, config: dict, core=None):
        """
        Khởi tạo service phân tích video

        Args:
            config: Dict cấu hình đầy đủ của ứng dụng
            core: Instance PixelleVideoCore (để truy cập ComfyKit dùng chung)
        """
        super().__init__(config, service_name="video_analysis", core=core)
    
    async def __call__(
        self,
        video_path: str,
        # Lựa chọn nguồn workflow
        source: Literal['runninghub', 'selfhost'] = 'runninghub',
        workflow: Optional[str] = None,
        # Kết nối ComfyUI (tùy chọn ghi đè)
        comfyui_url: Optional[str] = None,
        runninghub_api_key: Optional[str] = None,
        # Tham số workflow bổ sung
        **params
    ) -> str:
        """
        Phân tích một video bằng workflow

        Args:
            video_path: Đường dẫn tới file video (local hoặc URL)
            source: Nguồn workflow - 'runninghub' (cloud, mặc định) hoặc 'selfhost' (ComfyUI cục bộ)
            workflow: Tên file workflow (tùy chọn, ghi đè cách resolve theo source)
            comfyui_url: URL của ComfyUI (tùy chọn, ghi đè config)
            runninghub_api_key: API Key của RunningHub (tùy chọn, ghi đè config)
            **params: Tham số workflow bổ sung

        Returns:
            str: Mô tả văn bản về nội dung video

        Ví dụ:
            # Đơn giản nhất: dùng mặc định (runninghub cloud)
            description = await pixelle_video.video_analysis("temp/01_segment.mp4")

            # Dùng ComfyUI cục bộ (tương lai)
            description = await pixelle_video.video_analysis(
                "temp/01_segment.mp4",
                source="selfhost"
            )

            # Dùng workflow cụ thể (bỏ qua cơ chế resolve theo source)
            description = await pixelle_video.video_analysis(
                "temp/01_segment.mp4",
                workflow="runninghub/custom_video_analysis.json"
            )
        """
        from pixelle_video.utils.workflow_util import resolve_workflow_path

        # 1. Kiểm tra đường dẫn video
        video_path_obj = Path(video_path)
        if not video_path_obj.exists():
            raise FileNotFoundError(f"Không tìm thấy file video: {video_path}")

        # 2. Resolve đường dẫn workflow theo quy ước
        if workflow is None:
            # Dùng cách đặt tên chuẩn: {source}/analyse_video.json
            workflow = resolve_workflow_path("analyse_video", source)
            logger.info(f"Đang dùng workflow {source}: {workflow}")

        # 3. Resolve workflow (trả về thông tin có cấu trúc)
        workflow_info = self._resolve_workflow(workflow=workflow)

        # 4. Xây dựng tham số workflow
        workflow_params = {
            "video": str(video_path)  # Truyền đường dẫn video vào workflow
        }

        # Thêm bất kỳ tham số bổ sung nào
        workflow_params.update(params)

        logger.debug(f"Tham số workflow: {workflow_params}")

        # 5. Chạy workflow bằng instance ComfyKit dùng chung từ core
        try:
            # Lấy instance ComfyKit dùng chung (khởi tạo lazy + hot-reload config)
            kit = await self.core._get_or_create_comfykit()

            # Xác định nội dung truyền vào ComfyKit dựa trên source
            if workflow_info["source"] == "runninghub" and "workflow_id" in workflow_info:
                # RunningHub: truyền workflow_id
                workflow_input = workflow_info["workflow_id"]
                logger.info(f"Đang chạy workflow RunningHub: {workflow_input}")
            else:
                # Selfhost: truyền đường dẫn file
                workflow_input = workflow_info["path"]
                logger.info(f"Đang chạy workflow selfhost: {workflow_input}")

            # Bổ sung yêu cầu mô tả bằng tiếng Việt nếu workflow chấp nhận tham số prompt/instruction
            if "prompt" not in workflow_params and "instruction" not in workflow_params:
                workflow_params.setdefault(
                    "prompt",
                    "Hãy mô tả chi tiết nội dung video này bằng tiếng Việt, bao gồm bối cảnh, hành động, "
                    "đối tượng và không khí. Trả lời bằng tiếng Việt tự nhiên, mạch lạc."
                )

            result = await kit.execute(workflow_input, workflow_params)

            # 6. Trích xuất mô tả từ kết quả
            if result.status != "completed":
                error_msg = result.msg or "Lỗi không xác định"
                logger.error(f"Phân tích video thất bại: {error_msg}")
                raise Exception(f"Phân tích video thất bại: {error_msg}")

            # Trích xuất mô tả văn bản từ kết quả
            # Workflow hiểu video trả về văn bản trong mảng result.texts
            description = None

            # Định dạng 1: Mảng texts trực tiếp (phổ biến nhất với video understanding)
            if result.texts and len(result.texts) > 0:
                description = result.texts[0]
                logger.debug(f"Tìm thấy mô tả trong result.texts: {description[:100]}...")

            # Định dạng 2: Output selfhost (text trực tiếp trong outputs)
            # Định dạng: {'6': {'text': ['description text']}}
            elif result.outputs:
                for node_id, node_output in result.outputs.items():
                    if 'text' in node_output:
                        text_list = node_output['text']
                        if text_list and len(text_list) > 0:
                            description = text_list[0]
                            logger.debug(f"Tìm thấy mô tả trong outputs.text: {description[:100]}...")
                            break

            # Định dạng 3: raw_data của RunningHub (URL file văn bản)
            # Định dạng: {'raw_data': [{'fileUrl': 'https://...txt', 'fileType': 'txt', ...}]}
            if not description and result.outputs and 'raw_data' in result.outputs:
                raw_data = result.outputs['raw_data']
                if raw_data and len(raw_data) > 0:
                    # Tìm mục có file văn bản
                    for item in raw_data:
                        if item.get('fileType') == 'txt' and 'fileUrl' in item:
                            # Tải nội dung văn bản từ URL
                            import aiohttp
                            async with aiohttp.ClientSession() as session:
                                async with session.get(item['fileUrl']) as resp:
                                    if resp.status == 200:
                                        description = await resp.text()
                                        description = description.strip()
                                        logger.debug(f"Đã tải mô tả từ URL: {description[:100]}...")
                                        break

            if not description:
                logger.error(f"Không tìm thấy văn bản trong kết quả. Status: {result.status}, Outputs: {result.outputs}, Texts: {result.texts}")
                raise Exception("Không sinh được mô tả từ quá trình phân tích video")

            logger.info(f"✅ Đã phân tích video: {description[:100]}...")

            return description

        except Exception as e:
            logger.error(f"Lỗi phân tích video: {e}")
            raise
