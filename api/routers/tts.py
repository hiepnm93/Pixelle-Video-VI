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
Các endpoint TTS (Text-to-Speech)
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.schemas.tts import TTSSynthesizeRequest, TTSSynthesizeResponse
from pixelle_video.utils.tts_util import get_audio_duration

router = APIRouter(prefix="/tts", tags=["Basic Services"])


@router.post("/synthesize", response_model=TTSSynthesizeResponse)
async def tts_synthesize(
    request: TTSSynthesizeRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Endpoint tổng hợp TTS (Text-to-Speech)

    Chuyển văn bản thành audio giọng nói bằng các workflow ComfyUI.

    - **text**: Văn bản cần tổng hợp
    - **workflow**: Khoá workflow TTS (tuỳ chọn, dùng mặc định nếu không chỉ định)
    - **ref_audio**: Audio tham chiếu để nhân bản giọng (tuỳ chọn)
    - **voice_id**: (Đã lỗi thời) ID giọng để tương thích với phiên bản cũ

    Trả về đường dẫn tới file audio đã tạo và thời lượng.

    Ví dụ:
    ```json
    {
        "text": "Hello, welcome to Pixelle-Video!",
        "workflow": "runninghub/tts_edge.json"
    }
    ```

    Với nhân bản giọng:
    ```json
    {
        "text": "Hello, this is a cloned voice",
        "workflow": "runninghub/tts_index2.json",
        "ref_audio": "path/to/reference.wav"
    }
    ```
    """
    try:
        logger.info(f"Yêu cầu tổng hợp TTS: {request.text[:50]}...")

        # Xây dựng tham số TTS
        tts_params = {"text": request.text}

        # Thêm workflow nếu được chỉ định
        if request.workflow:
            tts_params["workflow"] = request.workflow

        # Thêm ref_audio nếu được chỉ định
        if request.ref_audio:
            tts_params["ref_audio"] = request.ref_audio

        # Hỗ trợ voice_id cũ (đã lỗi thời)
        if request.voice_id and not request.workflow:
            logger.warning("Tham số voice_id đã lỗi thời, vui lòng dùng workflow thay thế")
            tts_params["voice"] = request.voice_id

        # Gọi dịch vụ TTS
        audio_path = await pixelle_video.tts(**tts_params)

        # Lấy thời lượng audio
        duration = get_audio_duration(audio_path)

        return TTSSynthesizeResponse(
            audio_path=audio_path,
            duration=duration
        )

    except Exception as e:
        logger.error(f"Lỗi tổng hợp TTS: {e}")
        raise HTTPException(status_code=500, detail=str(e))

