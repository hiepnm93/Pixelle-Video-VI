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
Các endpoint LLM (Large Language Model)
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.schemas.llm import LLMChatRequest, LLMChatResponse

router = APIRouter(prefix="/llm", tags=["Basic Services"])


@router.post("/chat", response_model=LLMChatResponse)
async def llm_chat(
    request: LLMChatRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Endpoint chat LLM

    Tạo phản hồi văn bản bằng LLM đã cấu hình.

    - **prompt**: Prompt/câu hỏi của người dùng
    - **temperature**: Mức độ sáng tạo (0.0-2.0, thấp = ổn định hơn)
    - **max_tokens**: Độ dài phản hồi tối đa

    Trả về phản hồi văn bản đã tạo.
    """
    try:
        logger.info(f"Yêu cầu chat LLM: {request.prompt[:50]}...")

        # Gọi dịch vụ LLM
        response = await pixelle_video.llm(
            prompt=request.prompt,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )

        return LLMChatResponse(
            content=response,
            tokens_used=None  # Có thể thêm đếm token nếu cần
        )

    except Exception as e:
        logger.error(f"Lỗi chat LLM: {e}")
        raise HTTPException(status_code=500, detail=str(e))

