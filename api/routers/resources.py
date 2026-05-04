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
Các endpoint khám phá tài nguyên

Cung cấp endpoint để khám phá các workflow, template và BGM có sẵn.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.schemas.resources import (
    WorkflowInfo,
    WorkflowListResponse,
    TemplateInfo,
    TemplateListResponse,
    BGMInfo,
    BGMListResponse,
)
from pixelle_video.utils.os_util import list_resource_files, get_root_path, get_data_path
from pixelle_video.utils.template_util import get_all_templates_with_info

router = APIRouter(prefix="/resources", tags=["Resources"])


@router.get("/workflows/tts", response_model=WorkflowListResponse)
async def list_tts_workflows(pixelle_video: PixelleVideoDep):
    """
    Liệt kê các workflow TTS có sẵn

    Trả về danh sách workflow TTS từ cả nguồn RunningHub và self-hosted.

    Ví dụ phản hồi:
    ```json
    {
        "workflows": [
            {
                "name": "tts_edge.json",
                "display_name": "tts_edge.json - Runninghub",
                "source": "runninghub",
                "path": "workflows/runninghub/tts_edge.json",
                "key": "runninghub/tts_edge.json",
                "workflow_id": "123456"
            }
        ]
    }
    ```
    """
    try:
        # Lấy tất cả workflow từ dịch vụ TTS
        all_workflows = pixelle_video.tts.list_workflows()

        # Lọc chỉ lấy workflow TTS (tên file bắt đầu bằng "tts_")
        tts_workflows = [
            WorkflowInfo(**wf)
            for wf in all_workflows
            if wf["name"].startswith("tts_")
        ]

        return WorkflowListResponse(workflows=tts_workflows)

    except Exception as e:
        logger.error(f"Lỗi liệt kê workflow TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflows/media", response_model=WorkflowListResponse)
async def list_media_workflows(pixelle_video: PixelleVideoDep):
    """
    Liệt kê các workflow media có sẵn (cả ảnh và video)

    Trả về danh sách tất cả workflow media từ cả nguồn RunningHub và self-hosted.

    Ví dụ phản hồi:
    ```json
    {
        "workflows": [
            {
                "name": "image_flux.json",
                "display_name": "image_flux.json - Runninghub",
                "source": "runninghub",
                "path": "workflows/runninghub/image_flux.json",
                "key": "runninghub/image_flux.json",
                "workflow_id": "123456"
            },
            {
                "name": "video_wan2.1.json",
                "display_name": "video_wan2.1.json - Runninghub",
                "source": "runninghub",
                "path": "workflows/runninghub/video_wan2.1.json",
                "key": "runninghub/video_wan2.1.json",
                "workflow_id": "123457"
            }
        ]
    }
    ```
    """
    try:
        # Lấy tất cả workflow từ dịch vụ media (gồm cả ảnh và video)
        all_workflows = pixelle_video.media.list_workflows()

        media_workflows = [WorkflowInfo(**wf) for wf in all_workflows]

        return WorkflowListResponse(workflows=media_workflows)

    except Exception as e:
        logger.error(f"Lỗi liệt kê workflow media: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Giữ endpoint cũ để tương thích ngược
@router.get("/workflows/image", response_model=WorkflowListResponse)
async def list_image_workflows(pixelle_video: PixelleVideoDep):
    """
    Liệt kê các workflow ảnh có sẵn (đã lỗi thời, hãy dùng /workflows/media)

    Endpoint này được giữ để tương thích ngược nhưng chỉ lọc các workflow image_.
    """
    try:
        all_workflows = pixelle_video.media.list_workflows()

        # Lọc chỉ lấy workflow ảnh (tên file bắt đầu bằng "image_")
        image_workflows = [
            WorkflowInfo(**wf)
            for wf in all_workflows
            if wf["name"].startswith("image_")
        ]

        return WorkflowListResponse(workflows=image_workflows)

    except Exception as e:
        logger.error(f"Lỗi liệt kê workflow ảnh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=TemplateListResponse)
async def list_templates():
    """
    Liệt kê các template video có sẵn

    Trả về danh sách template HTML được nhóm theo kích thước (dọc, ngang, vuông).
    Các template được gộp từ cả thư mục mặc định (templates/) và tuỳ chỉnh (data/templates/).

    Ví dụ phản hồi:
    ```json
    {
        "templates": [
            {
                "name": "default.html",
                "display_name": "default.html",
                "size": "1080x1920",
                "width": 1080,
                "height": 1920,
                "orientation": "portrait",
                "path": "templates/1080x1920/default.html",
                "key": "1080x1920/default.html"
            }
        ]
    }
    ```
    """
    try:
        # Lấy tất cả template kèm thông tin
        all_templates = get_all_templates_with_info()

        # Chuyển sang định dạng phản hồi của API
        templates = []
        for t in all_templates:
            templates.append(TemplateInfo(
                name=t.display_info.name,
                display_name=t.display_info.name,
                size=t.display_info.size,
                width=t.display_info.width,
                height=t.display_info.height,
                orientation=t.display_info.orientation,
                path=t.template_path,
                key=t.template_path
            ))

        return TemplateListResponse(templates=templates)

    except Exception as e:
        logger.error(f"Lỗi liệt kê template: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/bgm", response_model=BGMListResponse)
async def list_bgm():
    """
    Liệt kê các file nhạc nền có sẵn

    Trả về danh sách file BGM được gộp từ cả thư mục mặc định (bgm/) và tuỳ chỉnh (data/bgm/).
    File tuỳ chỉnh ưu tiên hơn file mặc định trùng tên.

    Định dạng được hỗ trợ: mp3, wav, flac, m4a, aac, ogg

    Ví dụ phản hồi:
    ```json
    {
        "bgm_files": [
            {
                "name": "default.mp3",
                "path": "bgm/default.mp3",
                "source": "default"
            },
            {
                "name": "happy.mp3",
                "path": "data/bgm/happy.mp3",
                "source": "custom"
            }
        ]
    }
    ```
    """
    try:
        # Các phần mở rộng audio được hỗ trợ
        audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg')

        # Thu thập file BGM từ cả hai vị trí
        bgm_files_dict = {}  # {filename: {"path": str, "source": str}}

        # Quét thư mục bgm/ mặc định
        default_bgm_dir = Path(get_root_path("bgm"))
        if default_bgm_dir.exists() and default_bgm_dir.is_dir():
            for item in default_bgm_dir.iterdir():
                if item.is_file() and item.suffix.lower() in audio_extensions:
                    bgm_files_dict[item.name] = {
                        "path": f"bgm/{item.name}",
                        "source": "default"
                    }

        # Quét thư mục data/bgm/ tuỳ chỉnh (ghi đè mặc định)
        custom_bgm_dir = Path(get_data_path("bgm"))
        if custom_bgm_dir.exists() and custom_bgm_dir.is_dir():
            for item in custom_bgm_dir.iterdir():
                if item.is_file() and item.suffix.lower() in audio_extensions:
                    bgm_files_dict[item.name] = {
                        "path": f"data/bgm/{item.name}",
                        "source": "custom"
                    }

        # Chuyển sang định dạng phản hồi
        bgm_files = [
            BGMInfo(
                name=name,
                path=info["path"],
                source=info["source"]
            )
            for name, info in sorted(bgm_files_dict.items())
        ]

        return BGMListResponse(bgm_files=bgm_files)

    except Exception as e:
        logger.error(f"Lỗi liệt kê BGM: {e}")
        raise HTTPException(status_code=500, detail=str(e))
