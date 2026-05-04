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
Các endpoint tạo video

Hỗ trợ tạo video đồng bộ và bất đồng bộ.
"""

import os
from fastapi import APIRouter, HTTPException, Request
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.schemas.video import (
    VideoGenerateRequest,
    VideoGenerateResponse,
    VideoGenerateAsyncResponse,
)
from api.tasks import task_manager, TaskType

router = APIRouter(prefix="/video", tags=["Video Generation"])


def path_to_url(request: Request, file_path: str) -> str:
    """
    Chuyển đường dẫn file sang URL có thể truy cập

    Xử lý cả đường dẫn tuyệt đối và tương đối, trích xuất phần đường dẫn
    tương đối so với thư mục output để tạo URL.

    Args:
        request: Đối tượng Request của FastAPI (cung cấp base_url từ request thực tế)
        file_path: Đường dẫn file tuyệt đối hoặc tương đối

    Returns:
        URL đầy đủ để truy cập file

    Ví dụ:
        Windows: G:\\...\\output\\20251205_233630_c939\\final.mp4
              -> http://localhost:8000/api/files/20251205_233630_c939/final.mp4

        Linux:   /home/user/.../output/20251205_233630_c939/final.mp4
              -> http://localhost:8000/api/files/20251205_233630_c939/final.mp4

        Domain:  Với request có domain -> https://your-domain.com/api/files/...
    """
    from pathlib import Path
    import os

    # Chuẩn hoá dấu phân tách đường dẫn về dấu / (để tương thích đa nền tảng)
    file_path = file_path.replace("\\", "/")

    # Kiểm tra xem có phải đường dẫn tuyệt đối không (cả Windows và Linux)
    is_absolute = os.path.isabs(file_path) or Path(file_path).is_absolute()

    if is_absolute:
        # Tìm "output" trong đường dẫn và lấy tất cả phần sau nó
        # Tách theo / để hoạt động với đường dẫn đã chuẩn hoá
        parts = file_path.split("/")
        try:
            output_idx = parts.index("output")
            # Lấy tất cả các phần sau "output" và ghép lại
            relative_parts = parts[output_idx + 1:]
            file_path = "/".join(relative_parts)
        except ValueError:
            # Nếu "output" không có trong đường dẫn, chỉ dùng tên file
            file_path = Path(file_path).name
    else:
        # Nếu đường dẫn tương đối bắt đầu bằng "output/", loại bỏ nó
        if file_path.startswith("output/"):
            file_path = file_path[7:]  # Loại bỏ "output/"

    # Tạo URL dùng base_url của request (tự động khớp với host của request)
    base_url = str(request.base_url).rstrip('/')
    return f"{base_url}/api/files/{file_path}"


@router.post("/generate/sync", response_model=VideoGenerateResponse)
async def generate_video_sync(
    request_body: VideoGenerateRequest,
    pixelle_video: PixelleVideoDep,
    request: Request
):
    """
    Tạo video đồng bộ

    Endpoint này sẽ chặn (block) cho đến khi video được tạo xong.
    Phù hợp với video nhỏ (< 30 giây).

    **Lưu ý**: Có thể bị timeout với video lớn. Hãy dùng `/generate/async` thay thế.

    Body request bao gồm tất cả tham số tạo video.
    Xem schema VideoGenerateRequest để biết chi tiết.

    Trả về đường dẫn tới video đã tạo, thời lượng và kích thước file.
    """
    try:
        logger.info(f"Tạo video đồng bộ: {request_body.text[:50]}...")

        # Tự động xác định media_width và media_height từ thẻ meta của template (bắt buộc)
        if not request_body.frame_template:
            raise ValueError("frame_template là bắt buộc để xác định kích thước media")

        from pixelle_video.services.frame_html import HTMLFrameGenerator
        from pixelle_video.utils.template_util import resolve_template_path
        template_path = resolve_template_path(request_body.frame_template)
        generator = HTMLFrameGenerator(template_path)
        media_width, media_height = generator.get_media_size()
        logger.debug(f"Tự động xác định kích thước media từ template: {media_width}x{media_height}")

        # Xây dựng tham số tạo video
        video_params = {
            "text": request_body.text,
            "mode": request_body.mode,
            "title": request_body.title,
            "n_scenes": request_body.n_scenes,
            "min_narration_words": request_body.min_narration_words,
            "max_narration_words": request_body.max_narration_words,
            "min_image_prompt_words": request_body.min_image_prompt_words,
            "max_image_prompt_words": request_body.max_image_prompt_words,
            "media_width": media_width,
            "media_height": media_height,
            "media_workflow": request_body.media_workflow,
            "video_fps": request_body.video_fps,
            "frame_template": request_body.frame_template,
            "prompt_prefix": request_body.prompt_prefix,
            "bgm_path": request_body.bgm_path,
            "bgm_volume": request_body.bgm_volume,
        }

        # Thêm workflow TTS nếu được chỉ định
        if request_body.tts_workflow:
            video_params["tts_workflow"] = request_body.tts_workflow

        # Thêm ref_audio nếu được chỉ định
        if request_body.ref_audio:
            video_params["ref_audio"] = request_body.ref_audio

        # Hỗ trợ voice_id cũ (đã lỗi thời)
        if request_body.voice_id:
            logger.warning("Tham số voice_id đã lỗi thời, vui lòng dùng tts_workflow thay thế")
            video_params["voice_id"] = request_body.voice_id

        # Thêm tham số template tuỳ chỉnh nếu được chỉ định
        if request_body.template_params:
            video_params["template_params"] = request_body.template_params

        # Gọi dịch vụ tạo video
        result = await pixelle_video.generate_video(**video_params)

        # Lấy kích thước file
        file_size = os.path.getsize(result.video_path) if os.path.exists(result.video_path) else 0

        # Chuyển đường dẫn sang URL
        video_url = path_to_url(request, result.video_path)

        return VideoGenerateResponse(
            video_url=video_url,
            duration=result.duration,
            file_size=file_size
        )

    except Exception as e:
        logger.error(f"Lỗi tạo video đồng bộ: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate/async", response_model=VideoGenerateAsyncResponse)
async def generate_video_async(
    request_body: VideoGenerateRequest,
    pixelle_video: PixelleVideoDep,
    request: Request
):
    """
    Tạo video bất đồng bộ

    Tạo một task chạy nền để sinh video.
    Trả về ngay lập tức với task_id để theo dõi tiến trình.

    **Quy trình:**
    1. Gửi yêu cầu tạo video
    2. Nhận task_id trong phản hồi
    3. Poll `/api/tasks/{task_id}` để kiểm tra trạng thái
    4. Khi trạng thái là "completed", lấy video từ kết quả

    Body request bao gồm tất cả tham số tạo video.
    Xem schema VideoGenerateRequest để biết chi tiết.

    Trả về task_id để theo dõi tiến trình.
    """
    try:
        logger.info(f"Tạo video bất đồng bộ: {request_body.text[:50]}...")

        # Tạo task
        task = task_manager.create_task(
            task_type=TaskType.VIDEO_GENERATION,
            request_params=request_body.model_dump()
        )

        # Định nghĩa hàm thực thi bất đồng bộ
        async def execute_video_generation():
            """Thực thi tạo video chạy nền"""
            # Tự động xác định media_width và media_height từ thẻ meta của template (bắt buộc)
            if not request_body.frame_template:
                raise ValueError("frame_template là bắt buộc để xác định kích thước media")

            from pixelle_video.services.frame_html import HTMLFrameGenerator
            from pixelle_video.utils.template_util import resolve_template_path
            template_path = resolve_template_path(request_body.frame_template)
            generator = HTMLFrameGenerator(template_path)
            media_width, media_height = generator.get_media_size()
            logger.debug(f"Tự động xác định kích thước media từ template: {media_width}x{media_height}")

            # Xây dựng tham số tạo video
            video_params = {
                "text": request_body.text,
                "mode": request_body.mode,
                "title": request_body.title,
                "n_scenes": request_body.n_scenes,
                "min_narration_words": request_body.min_narration_words,
                "max_narration_words": request_body.max_narration_words,
                "min_image_prompt_words": request_body.min_image_prompt_words,
                "max_image_prompt_words": request_body.max_image_prompt_words,
                "media_width": media_width,
                "media_height": media_height,
                "media_workflow": request_body.media_workflow,
                "video_fps": request_body.video_fps,
                "frame_template": request_body.frame_template,
                "prompt_prefix": request_body.prompt_prefix,
                "bgm_path": request_body.bgm_path,
                "bgm_volume": request_body.bgm_volume,
                # Có thể thêm progress callback ở đây nếu cần
                # "progress_callback": lambda event: task_manager.update_progress(...)
            }

            # Thêm workflow TTS nếu được chỉ định
            if request_body.tts_workflow:
                video_params["tts_workflow"] = request_body.tts_workflow

            # Thêm ref_audio nếu được chỉ định
            if request_body.ref_audio:
                video_params["ref_audio"] = request_body.ref_audio

            # Hỗ trợ voice_id cũ (đã lỗi thời)
            if request_body.voice_id:
                logger.warning("Tham số voice_id đã lỗi thời, vui lòng dùng tts_workflow thay thế")
                video_params["voice_id"] = request_body.voice_id

            # Thêm tham số template tuỳ chỉnh nếu được chỉ định
            if request_body.template_params:
                video_params["template_params"] = request_body.template_params

            result = await pixelle_video.generate_video(**video_params)

            # Lấy kích thước file
            file_size = os.path.getsize(result.video_path) if os.path.exists(result.video_path) else 0

            # Chuyển đường dẫn sang URL
            video_url = path_to_url(request, result.video_path)

            return {
                "video_url": video_url,
                "duration": result.duration,
                "file_size": file_size
            }

        # Bắt đầu thực thi
        await task_manager.execute_task(
            task_id=task.task_id,
            coro_func=execute_video_generation
        )

        return VideoGenerateAsyncResponse(
            task_id=task.task_id
        )

    except Exception as e:
        logger.error(f"Lỗi tạo video bất đồng bộ: {e}")
        raise HTTPException(status_code=500, detail=str(e))
