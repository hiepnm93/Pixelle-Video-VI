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
Service cơ sở cho ComfyUI - Logic chung cho các service dựa trên ComfyUI
"""

import json
import os
from pathlib import Path
from typing import Optional, List, Dict, Any

from comfykit import ComfyKit
from loguru import logger

from pixelle_video.utils.os_util import (
    get_resource_path,
    list_resource_files,
    list_resource_dirs
)


class ComfyBaseService:
    """
    Service cơ sở cho các tính năng dựa trên workflow ComfyUI

    Cung cấp chức năng chung cho TTS, Image và các service ComfyUI khác.

    Các subclass nên định nghĩa:
    - WORKFLOW_PREFIX: Tiền tố cho file workflow (vd: "image_", "tts_")
    - DEFAULT_WORKFLOW: Tên file workflow mặc định (vd: "image_flux.json")
    - WORKFLOWS_DIR: Thư mục chứa workflow (mặc định: "workflows")
    """

    WORKFLOW_PREFIX: str = ""  # Phải được override bởi subclass
    DEFAULT_WORKFLOW: str = ""  # Phải được override bởi subclass
    WORKFLOWS_DIR: str = "workflows"

    def __init__(self, config: dict, service_name: str, core=None):
        """
        Khởi tạo service cơ sở ComfyUI

        Args:
            config: Dict cấu hình đầy đủ của ứng dụng
            service_name: Tên service trong config (vd: "tts", "image")
            core: Instance PixelleVideoCore (để truy cập ComfyKit dùng chung)
        """
        # Cấu hình riêng cho service (vd: config["comfyui"]["tts"])
        comfyui_config = config.get("comfyui", {})
        self.config = comfyui_config.get(service_name, {})

        # Cấu hình ComfyUI toàn cục (cho comfyui_url và runninghub_api_key)
        self.global_config = comfyui_config

        self.service_name = service_name
        self._workflows_cache: Optional[List[str]] = None

        # Tham chiếu tới core (để truy cập ComfyKit dùng chung)
        self.core = core
    
    def _scan_workflows(self) -> List[Dict[str, Any]]:
        """
        Quét các file workflows/source/*.json từ mọi thư mục nguồn (gộp từ workflows/ và data/workflows/)

        Returns:
            Danh sách dict thông tin workflow
            Example: [
                {
                    "name": "image_flux.json",
                    "display_name": "image_flux.json - Selfhost",
                    "source": "selfhost",
                    "path": "workflows/selfhost/image_flux.json",
                    "key": "selfhost/image_flux.json"
                },
                {
                    "name": "image_flux.json",
                    "display_name": "image_flux.json - Runninghub", 
                    "source": "runninghub",
                    "path": "workflows/runninghub/image_flux.json",
                    "key": "runninghub/image_flux.json",
                    "workflow_id": "123456"
                }
            ]
        """
        workflows = []

        # Lấy tất cả thư mục nguồn workflow (gộp từ workflows/ và data/workflows/)
        source_dirs = list_resource_dirs("workflows")

        if not source_dirs:
            logger.warning("Không tìm thấy thư mục nguồn workflow nào")
            return workflows

        # Quét từng thư mục nguồn để tìm file workflow
        for source_name in source_dirs:
            # Lấy tất cả file JSON cho nguồn này (gộp từ cả hai vị trí)
            workflow_files = list_resource_files("workflows", source_name)

            # Lọc chỉ các file khớp với tiền tố
            matching_files = [
                f for f in workflow_files
                if f.startswith(self.WORKFLOW_PREFIX) and f.endswith('.json')
            ]

            for filename in matching_files:
                try:
                    # Lấy đường dẫn file thực tế (tuỳ chỉnh > mặc định)
                    file_path = Path(get_resource_path("workflows", source_name, filename))
                    workflow_info = self._parse_workflow_file(file_path, source_name)
                    workflows.append(workflow_info)
                    logger.debug(f"Tìm thấy workflow: {workflow_info['key']}")
                except Exception as e:
                    logger.error(f"Không thể parse workflow {source_name}/{filename}: {e}")

        # Sắp xếp theo key (source/name)
        return sorted(workflows, key=lambda w: w["key"])

    def _parse_workflow_file(self, file_path: Path, source: str) -> Dict[str, Any]:
        """
        Parse file workflow và trích xuất metadata

        Args:
            file_path: Đường dẫn tới file JSON workflow
            source: Tên thư mục nguồn (vd: "selfhost", "runninghub")

        Returns:
            Workflow info dict with structure:
            {
                "name": "image_flux.json",
                "display_name": "image_flux.json - Runninghub",
                "source": "runninghub",
                "path": "workflows/runninghub/image_flux.json",
                "key": "runninghub/image_flux.json",
                "workflow_id": "123456"  # Only for RunningHub
            }
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = json.load(f)

        # Xây dựng thông tin cơ sở
        workflow_info = {
            "name": file_path.name,
            "display_name": f"{file_path.name} - {source.title()}",
            "source": source,
            "path": str(file_path),
            "key": f"{source}/{file_path.name}"
        }

        # Kiểm tra xem có phải định dạng wrapper không (RunningHub, v.v.)
        if "source" in content:
            # Định dạng wrapper: {"source": "runninghub", "workflow_id": "xxx", ...}
            if "workflow_id" in content:
                workflow_info["workflow_id"] = content["workflow_id"]

        return workflow_info

    def _get_default_workflow(self) -> str:
        """
        Lấy workflow mặc định từ config (bắt buộc, không có dự phòng)

        Returns:
            Key workflow mặc định (vd: "runninghub/image_flux.json")

        Raises:
            ValueError: Nếu default_workflow chưa được cấu hình
        """
        default_workflow = self.config.get("default_workflow")

        if not default_workflow:
            raise ValueError(
                f"Chưa cấu hình workflow mặc định cho {self.service_name}. "
                f"Vui lòng đặt 'default_workflow' trong config.yaml dưới mục '{self.service_name}'. "
                f"Workflow có sẵn: {', '.join(self.available)}"
            )

        return default_workflow

    def _resolve_workflow(self, workflow: Optional[str] = None) -> Dict[str, Any]:
        """
        Phân giải key workflow thành thông tin workflow

        Args:
            workflow: Key workflow (vd: "runninghub/image_flux.json")
                     Nếu None, dùng mặc định từ config

        Returns:
            Workflow info dict with structure:
            {
                "name": "image_flux.json",
                "display_name": "image_flux.json - Runninghub",
                "source": "runninghub",
                "path": "workflows/runninghub/image_flux.json",
                "key": "runninghub/image_flux.json",
                "workflow_id": "123456"  # Only for RunningHub
            }
        
        Raises:
            ValueError: Nếu không tìm thấy workflow
        """
        # 1. Nếu không chỉ định, dùng mặc định từ config
        if workflow is None:
            workflow = self._get_default_workflow()

        # 2. Quét các workflow có sẵn
        available_workflows = self._scan_workflows()

        # 3. Tìm workflow khớp theo key
        for wf_info in available_workflows:
            if wf_info["key"] == workflow:
                logger.info(f"🎬 Đang dùng workflow {self.service_name}: {workflow}")
                return wf_info

        # 4. Không tìm thấy - sinh thông báo lỗi
        available_keys = [wf["key"] for wf in available_workflows]
        available_str = ", ".join(available_keys) if available_keys else "không có"
        raise ValueError(
            f"Không tìm thấy workflow '{workflow}'. "
            f"Workflow có sẵn: {available_str}"
        )

    def _prepare_comfykit_config(
        self,
        comfyui_url: Optional[str] = None,
        runninghub_api_key: Optional[str] = None,
        runninghub_instance_type: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Chuẩn bị cấu hình ComfyKit

        Args:
            comfyui_url: URL ComfyUI (tuỳ chọn, ghi đè config)
            runninghub_api_key: API key RunningHub (tuỳ chọn, ghi đè config)
            runninghub_instance_type: Kiểu instance RunningHub (tuỳ chọn, ghi đè config)

        Returns:
            Dict cấu hình ComfyKit
        """
        kit_config = {}

        # URL ComfyUI (ưu tiên: tham số > config toàn cục > env > mặc định)
        final_comfyui_url = (
            comfyui_url 
            or self.global_config.get("comfyui_url")
            or os.getenv("COMFYUI_BASE_URL")
            or "http://127.0.0.1:8188"
        )
        kit_config["comfyui_url"] = final_comfyui_url

        # API key RunningHub (ưu tiên: tham số > config toàn cục > env)
        final_rh_key = (
            runninghub_api_key
            or self.global_config.get("runninghub_api_key")
            or os.getenv("RUNNINGHUB_API_KEY")
        )
        if final_rh_key:
            kit_config["runninghub_api_key"] = final_rh_key

        # Kiểu instance RunningHub (ưu tiên: tham số > config toàn cục > env)
        # Chỉ truyền nếu có giá trị không rỗng
        final_instance_type = (
            runninghub_instance_type
            or self.global_config.get("runninghub_instance_type")
            or os.getenv("RUNNINGHUB_INSTANCE_TYPE")
        )
        if final_instance_type and final_instance_type.strip():
            kit_config["runninghub_instance_type"] = final_instance_type

        logger.debug(f"Cấu hình ComfyKit: {kit_config}")
        return kit_config

    def list_workflows(self) -> List[Dict[str, Any]]:
        """
        Liệt kê tất cả workflow có sẵn kèm metadata đầy đủ

        Returns:
            Danh sách dict thông tin workflow (đã sắp xếp theo key)

        Ví dụ:
            workflows = service.list_workflows()
            # [
            #     {
            #         "name": "image_flux.json",
            #         "display_name": "image_flux.json - Runninghub",
            #         "source": "runninghub",
            #         "path": "workflows/runninghub/image_flux.json",
            #         "key": "runninghub/image_flux.json",
            #         "workflow_id": "123456"
            #     },
            #     ...
            # ]
        """
        return self._scan_workflows()
    
    @property
    def available(self) -> List[str]:
        """
        Liệt kê các key workflow có sẵn

        Returns:
            Danh sách key workflow có sẵn (vd: ["runninghub/image_flux.json", ...])

        Ví dụ:
            print(f"Workflow có sẵn: {service.available}")
        """
        workflows = self.list_workflows()
        return [wf["key"] for wf in workflows]

    def __repr__(self) -> str:
        """Biểu diễn dạng chuỗi"""
        default = self._get_default_workflow()
        available = ", ".join(self.available) if self.available else "không có"
        return (
            f"<{self.__class__.__name__} "
            f"default={default!r} "
            f"available=[{available}]>"
        )

