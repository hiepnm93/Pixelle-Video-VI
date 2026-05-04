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
Service phân tích ảnh - Triển khai dựa trên Workflow ComfyUI

Sử dụng Florence-2 hoặc các model thị giác khác để phân tích ảnh và sinh mô tả.
"""

from typing import Optional, Literal
from pathlib import Path

from comfykit import ComfyKit
from loguru import logger

from pixelle_video.services.comfy_base_service import ComfyBaseService


class ImageAnalysisService(ComfyBaseService):
    """
    Service phân tích ảnh - Dựa trên Workflow

    Dùng ComfyKit để thực thi các workflow phân tích ảnh (vd: Florence-2, BLIP, v.v.).
    Trả về mô tả văn bản chi tiết của ảnh.

    Quy ước: workflow theo mẫu {source}/analyse_image.json
    - runninghub/analyse_image.json (mặc định, dựa trên cloud)
    - selfhost/analyse_image.json (ComfyUI local)

    Cách dùng:
        # Dùng mặc định (cloud runninghub)
        description = await pixelle_video.image_analysis("path/to/image.jpg")

        # Dùng ComfyUI local
        description = await pixelle_video.image_analysis(
            "path/to/image.jpg",
            source="selfhost"
        )

        # Liệt kê các workflow có sẵn
        workflows = pixelle_video.image_analysis.list_workflows()
    """
    
    WORKFLOW_PREFIX = "analyse_"
    WORKFLOWS_DIR = "workflows"
    
    def __init__(self, config: dict, core=None):
        """
        Khởi tạo service phân tích ảnh

        Args:
            config: Dict cấu hình đầy đủ của ứng dụng
            core: Instance PixelleVideoCore (để truy cập ComfyKit dùng chung)
        """
        super().__init__(config, service_name="image_analysis", core=core)
    
    async def __call__(
        self,
        image_path: str,
        # Workflow source selection
        source: Literal['runninghub', 'selfhost'] = 'runninghub',
        workflow: Optional[str] = None,
        # ComfyUI connection (optional overrides)
        comfyui_url: Optional[str] = None,
        runninghub_api_key: Optional[str] = None,
        # Additional workflow parameters
        **params
    ) -> str:
        """
        Phân tích ảnh bằng workflow

        Args:
            image_path: Đường dẫn tới file ảnh (local hoặc URL)
            source: Nguồn workflow - 'runninghub' (cloud, mặc định) hoặc 'selfhost' (ComfyUI local)
            workflow: Tên file workflow (tuỳ chọn, ghi đè phân giải dựa trên source)
            comfyui_url: URL ComfyUI (tuỳ chọn, ghi đè config)
            runninghub_api_key: API key RunningHub (tuỳ chọn, ghi đè config)
            **params: Tham số workflow bổ sung

        Returns:
            str: Mô tả văn bản của ảnh

        Ví dụ:
            # Đơn giản nhất: dùng mặc định (cloud runninghub)
            description = await pixelle_video.image_analysis("temp/06.JPG")

            # Dùng ComfyUI local
            description = await pixelle_video.image_analysis(
                "temp/06.JPG",
                source="selfhost"
            )

            # Dùng workflow cụ thể (bỏ qua phân giải dựa trên source)
            description = await pixelle_video.image_analysis(
                "temp/06.JPG",
                workflow="selfhost/custom_analysis.json"
            )
        """
        from pixelle_video.utils.workflow_util import resolve_workflow_path

        # 1. Xác thực đường dẫn ảnh
        image_path_obj = Path(image_path)
        if not image_path_obj.exists():
            raise FileNotFoundError(f"Không tìm thấy file ảnh: {image_path}")

        # 2. Phân giải đường dẫn workflow theo quy ước
        if workflow is None:
            # Dùng tên chuẩn hoá: {source}/analyse_image.json
            workflow = resolve_workflow_path("analyse_image", source)
            logger.info(f"Đang dùng workflow {source}: {workflow}")

        # 2. Phân giải workflow (trả về thông tin có cấu trúc)
        workflow_info = self._resolve_workflow(workflow=workflow)

        # 3. Xây dựng tham số workflow
        workflow_params = {
            "image": str(image_path)  # Truyền đường dẫn ảnh tới workflow
        }

        # Thêm các tham số bổ sung
        workflow_params.update(params)

        logger.debug(f"Tham số workflow: {workflow_params}")

        # 4. Thực thi workflow dùng instance ComfyKit dùng chung từ core
        try:
            # Lấy instance ComfyKit dùng chung (khởi tạo lười + hot-reload config)
            kit = await self.core._get_or_create_comfykit()

            # Xác định truyền gì cho ComfyKit dựa trên source
            if workflow_info["source"] == "runninghub" and "workflow_id" in workflow_info:
                # RunningHub: truyền workflow_id
                workflow_input = workflow_info["workflow_id"]
                logger.info(f"Đang thực thi workflow RunningHub: {workflow_input}")
            else:
                # Selfhost: truyền đường dẫn file
                workflow_input = workflow_info["path"]
                logger.info(f"Đang thực thi workflow selfhost: {workflow_input}")

            result = await kit.execute(workflow_input, workflow_params)

            # 5. Trích xuất mô tả từ kết quả
            if result.status != "completed":
                error_msg = result.msg or "Lỗi không xác định"
                logger.error(f"Phân tích ảnh thất bại: {error_msg}")
                raise Exception(f"Phân tích ảnh thất bại: {error_msg}")

            # Trích xuất mô tả văn bản từ kết quả (định dạng tuỳ thuộc vào source)
            description = None

            # Thử định dạng 1: Output selfhost (text trực tiếp trong outputs)
            # Định dạng: {'6': {'text': ['nội dung mô tả']}}
            if result.outputs:
                for node_id, node_output in result.outputs.items():
                    if 'text' in node_output:
                        text_list = node_output['text']
                        if text_list and len(text_list) > 0:
                            description = text_list[0]
                            break

            # Thử định dạng 2: raw_data của RunningHub (URL file text)
            # Định dạng: {'raw_data': [{'fileUrl': 'https://...txt', 'fileType': 'txt', ...}]}
            if not description and result.outputs and 'raw_data' in result.outputs:
                raw_data = result.outputs['raw_data']
                if raw_data and len(raw_data) > 0:
                    # Tìm entry file text
                    for item in raw_data:
                        if item.get('fileType') == 'txt' and 'fileUrl' in item:
                            # Tải nội dung text từ URL
                            import aiohttp
                            async with aiohttp.ClientSession() as session:
                                async with session.get(item['fileUrl']) as resp:
                                    if resp.status == 200:
                                        description = await resp.text()
                                        description = description.strip()
                                        break

            if not description:
                logger.error(f"Không tìm thấy text trong outputs: {result.outputs}")
                raise Exception("Không sinh được mô tả")

            logger.info(f"✅ Đã phân tích ảnh: {description[:100]}...")

            return description

        except Exception as e:
            logger.error(f"Lỗi phân tích ảnh: {e}")
            raise
