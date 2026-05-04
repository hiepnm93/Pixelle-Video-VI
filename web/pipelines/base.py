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
Base & Registry cho Pipeline UI

Định nghĩa protocol PipelineUI và cơ chế đăng ký.
"""

from typing import Dict, Any, List, Type

class PipelineUI:
    """
    Lớp cơ sở cho các plugin Pipeline UI.

    Mỗi pipeline nên cài đặt một lớp con để định nghĩa UI đầy đủ trang của riêng nó.
    """
    name: str = "base"
    display_name: str = "Base Pipeline"
    icon: str = "🔌"
    description: str = ""

    def render(self, pixelle_video: Any):
        """
        Render toàn bộ nội dung trang cho pipeline này (bên dưới phần settings).

        Args:
            pixelle_video: Instance PixelleVideoCore đã được khởi tạo.
        """
        raise NotImplementedError


# ==================== Registry ====================

_pipeline_uis: Dict[str, PipelineUI] = {}

def register_pipeline_ui(ui_class: Type[PipelineUI]):
    """Đăng ký một lớp pipeline UI"""
    instance = ui_class()
    _pipeline_uis[instance.name] = instance

def get_pipeline_ui(name: str) -> PipelineUI:
    """Lấy instance pipeline UI theo tên"""
    return _pipeline_uis.get(name)

def get_all_pipeline_uis() -> List[PipelineUI]:
    """Lấy tất cả instance pipeline UI đã đăng ký"""
    return list(_pipeline_uis.values())
