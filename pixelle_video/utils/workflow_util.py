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
Bộ phân giải đường dẫn Workflow

Phân giải đường dẫn workflow chuẩn hoá cho tất cả service ComfyUI.
Quy ước: {source}/{service}.json

Ví dụ:
    - Phân tích ảnh: selfhost/analyse_image.json, runninghub/analyse_image.json
    - Sinh ảnh: selfhost/image.json, runninghub/image.json
    - Sinh video: selfhost/video.json, runninghub/video.json
    - TTS: selfhost/tts.json, runninghub/tts.json
"""

from typing import Literal

WorkflowSource = Literal['runninghub', 'selfhost']


def resolve_workflow_path(
    service_name: str,
    source: WorkflowSource = 'runninghub'
) -> str:
    """
    Phân giải đường dẫn workflow dùng quy ước đặt tên chuẩn hoá

    Quy ước: workflows/{source}/{service_name}.json

    Args:
        service_name: Định danh service (vd: "analyse_image", "image", "video", "tts")
        source: Nguồn workflow - 'runninghub' (mặc định) hoặc 'selfhost'

    Returns:
        Đường dẫn workflow theo định dạng: "{source}/{service_name}.json"

    Ví dụ:
        >>> resolve_workflow_path("analyse_image", "runninghub")
        'runninghub/analyse_image.json'

        >>> resolve_workflow_path("analyse_image", "selfhost")
        'selfhost/analyse_image.json'

        >>> resolve_workflow_path("image")  # mặc định runninghub
        'runninghub/image.json'
    """
    return f"{source}/{service_name}.json"


def get_default_source() -> WorkflowSource:
    """
    Lấy nguồn workflow mặc định

    Returns:
        'runninghub' - Cách tiếp cận ưu tiên cloud, tốt hơn cho người mới
    """
    return 'runninghub'
