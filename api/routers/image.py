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
Các endpoint tạo ảnh
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.schemas.image import ImageGenerateRequest, ImageGenerateResponse

router = APIRouter(prefix="/image", tags=["Basic Services"])


@router.post("/generate", response_model=ImageGenerateResponse)
async def image_generate(
    request: ImageGenerateRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Endpoint tạo ảnh

    Tạo ảnh từ prompt văn bản bằng ComfyKit.

    - **prompt**: Mô tả/prompt cho ảnh
    - **width**: Chiều rộng ảnh (512-2048)
    - **height**: Chiều cao ảnh (512-2048)
    - **workflow**: Tên file workflow tuỳ chỉnh (tuỳ chọn)

    Trả về đường dẫn tới ảnh đã tạo.
    """
    try:
        logger.info(f"Yêu cầu tạo ảnh: {request.prompt[:50]}...")

        # Gọi dịch vụ media (tương thích ngược với API image)
        media_result = await pixelle_video.media(
            prompt=request.prompt,
            width=request.width,
            height=request.height,
            workflow=request.workflow
        )

        # Để tương thích ngược, endpoint /image chỉ hỗ trợ kết quả là ảnh
        if media_result.is_video:
            raise HTTPException(
                status_code=400,
                detail="Workflow video đã được sử dụng. Vui lòng dùng endpoint /media/generate để tạo video."
            )

        return ImageGenerateResponse(
            image_path=media_result.url
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi tạo ảnh: {e}")
        raise HTTPException(status_code=500, detail=str(e))

