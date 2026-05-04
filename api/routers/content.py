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
Các endpoint tạo nội dung

Endpoint dùng để tạo lời thoại, prompt ảnh và tiêu đề.
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.schemas.content import (
    NarrationGenerateRequest,
    NarrationGenerateResponse,
    ImagePromptGenerateRequest,
    ImagePromptGenerateResponse,
    TitleGenerateRequest,
    TitleGenerateResponse,
)
from pixelle_video.utils.content_generators import (
    generate_narrations_from_topic,
    generate_image_prompts,
    generate_title,
)

router = APIRouter(prefix="/content", tags=["Content Generation"])


@router.post("/narration", response_model=NarrationGenerateResponse)
async def generate_narration(
    request: NarrationGenerateRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Tạo lời thoại từ văn bản

    Dùng LLM để tách văn bản thành nhiều đoạn lời thoại.

    - **text**: Văn bản nguồn
    - **n_scenes**: Số lượng lời thoại cần tạo
    - **min_words**: Số từ tối thiểu mỗi lời thoại
    - **max_words**: Số từ tối đa mỗi lời thoại

    Trả về danh sách các chuỗi lời thoại.
    """
    try:
        logger.info(f"Đang tạo {request.n_scenes} lời thoại từ văn bản")

        # Gọi hàm tiện ích tạo lời thoại
        narrations = await generate_narrations_from_topic(
            llm_service=pixelle_video.llm,
            topic=request.text,
            n_scenes=request.n_scenes,
            min_words=request.min_words,
            max_words=request.max_words
        )

        return NarrationGenerateResponse(
            narrations=narrations
        )

    except Exception as e:
        logger.error(f"Lỗi tạo lời thoại: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/image-prompt", response_model=ImagePromptGenerateResponse)
async def generate_image_prompt(
    request: ImagePromptGenerateRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Tạo prompt ảnh từ lời thoại

    Dùng LLM để tạo các prompt tạo ảnh chi tiết.

    - **narrations**: Danh sách các lời thoại
    - **min_words**: Số từ tối thiểu mỗi prompt
    - **max_words**: Số từ tối đa mỗi prompt

    Trả về danh sách các prompt ảnh.
    """
    try:
        logger.info(f"Đang tạo prompt ảnh cho {len(request.narrations)} lời thoại")

        # Gọi hàm tiện ích tạo prompt ảnh
        image_prompts = await generate_image_prompts(
            llm_service=pixelle_video.llm,
            narrations=request.narrations,
            min_words=request.min_words,
            max_words=request.max_words
        )

        return ImagePromptGenerateResponse(
            image_prompts=image_prompts
        )

    except Exception as e:
        logger.error(f"Lỗi tạo prompt ảnh: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/title", response_model=TitleGenerateResponse)
async def generate_title_endpoint(
    request: TitleGenerateRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Tạo tiêu đề video từ văn bản

    Dùng LLM để tạo một tiêu đề hấp dẫn.

    - **text**: Văn bản nguồn
    - **style**: Gợi ý phong cách tiêu đề (tuỳ chọn)

    Trả về tiêu đề đã tạo.
    """
    try:
        logger.info("Đang tạo tiêu đề từ văn bản")

        # Gọi hàm tiện ích tạo tiêu đề
        title = await generate_title(
            llm_service=pixelle_video.llm,
            content=request.text,
            strategy="llm"
        )

        return TitleGenerateResponse(
            title=title
        )

    except Exception as e:
        logger.error(f"Lỗi tạo tiêu đề: {e}")
        raise HTTPException(status_code=500, detail=str(e))

