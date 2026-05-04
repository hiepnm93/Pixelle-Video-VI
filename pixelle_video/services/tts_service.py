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
Service TTS (Text-to-Speech) - Hỗ trợ cả inference local và ComfyUI
"""

import os
import uuid
from pathlib import Path
from typing import Optional

from comfykit import ComfyKit
from loguru import logger

from pixelle_video.services.comfy_base_service import ComfyBaseService
from pixelle_video.utils.tts_util import edge_tts
from pixelle_video.tts_voices import speed_to_rate


class TTSService(ComfyBaseService):
    """
    Service TTS (Text-to-Speech) - Dựa trên Workflow

    Dùng ComfyKit để thực thi các workflow TTS.

    Cách dùng:
        # Dùng workflow mặc định
        audio_path = await pixelle_video.tts(text="Xin chào, thế giới!")

        # Dùng workflow cụ thể
        audio_path = await pixelle_video.tts(
            text="你好，世界！",
            workflow="tts_edge.json"
        )

        # Liệt kê các workflow có sẵn
        workflows = pixelle_video.tts.list_workflows()
    """

    WORKFLOW_PREFIX = "tts_"
    DEFAULT_WORKFLOW = None  # Không có mặc định hardcode, phải được cấu hình
    WORKFLOWS_DIR = "workflows"

    def __init__(self, config: dict, core=None):
        """
        Khởi tạo service TTS

        Args:
            config: Dict cấu hình đầy đủ của ứng dụng
            core: Instance PixelleVideoCore (để truy cập ComfyKit dùng chung)
        """
        super().__init__(config, service_name="tts", core=core)
    
    
    async def __call__(
        self,
        text: str,
        workflow: Optional[str] = None,
        # ComfyUI connection (optional overrides)
        comfyui_url: Optional[str] = None,
        runninghub_api_key: Optional[str] = None,
        # TTS parameters
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        # Inference mode override
        inference_mode: Optional[str] = None,
        # Output path
        output_path: Optional[str] = None,
        **params
    ) -> str:
        """
        Sinh giọng nói dùng Edge TTS local hoặc workflow ComfyUI

        Args:
            text: Văn bản cần chuyển thành giọng nói
            workflow: Tên file workflow (cho chế độ ComfyUI, mặc định: từ config)
            comfyui_url: URL ComfyUI (tuỳ chọn, ghi đè config)
            runninghub_api_key: API key RunningHub (tuỳ chọn, ghi đè config)
            voice: ID giọng (chế độ local: voice ID Edge TTS; ComfyUI: theo workflow)
            speed: Hệ số tốc độ đọc (1.0 = bình thường, >1.0 = nhanh hơn, <1.0 = chậm hơn)
            inference_mode: Ghi đè chế độ inference ("local" hoặc "comfyui", mặc định: từ config)
            output_path: Đường dẫn output tuỳ chỉnh (tự sinh nếu None)
            **params: Tham số workflow bổ sung

        Returns:
            Đường dẫn file audio đã sinh

        Ví dụ:
            # Inference local (Edge TTS)
            audio_path = await pixelle_video.tts(
                text="Xin chào, thế giới!",
                inference_mode="local",
                voice="zh-CN-YunjianNeural",
                speed=1.2
            )

            # Inference ComfyUI
            audio_path = await pixelle_video.tts(
                text="你好，世界！",
                inference_mode="comfyui",
                workflow="runninghub/tts_edge.json"
            )
        """
        # Xác định chế độ inference (tham số > config)
        mode = inference_mode or self.config.get("inference_mode", "local")

        # Định tuyến tới triển khai phù hợp
        if mode == "local":
            return await self._call_local_tts(
                text=text,
                voice=voice,
                speed=speed,
                output_path=output_path
            )
        else:  # comfyui
            # 1. Phân giải workflow (trả về thông tin có cấu trúc)
            workflow_info = self._resolve_workflow(workflow=workflow)

            # 2. Thực thi workflow ComfyUI
            return await self._call_comfyui_workflow(
                workflow_info=workflow_info,
                text=text,
                comfyui_url=comfyui_url,
                runninghub_api_key=runninghub_api_key,
                voice=voice,
                speed=speed,
                output_path=output_path,
                **params
            )
    
    async def _call_local_tts(
        self,
        text: str,
        voice: Optional[str] = None,
        speed: Optional[float] = None,
        output_path: Optional[str] = None,
    ) -> str:
        """
        Sinh giọng nói dùng Edge TTS local

        Args:
            text: Văn bản cần chuyển thành giọng nói
            voice: ID giọng Edge TTS (mặc định: từ config)
            speed: Hệ số tốc độ đọc (mặc định: từ config)
            output_path: Đường dẫn output tuỳ chỉnh (tự sinh nếu None)

        Returns:
            Đường dẫn file audio đã sinh
        """
        # Lấy mặc định từ config
        local_config = self.config.get("local", {})

        # Xác định voice và speed (tham số > config)
        final_voice = voice or local_config.get("voice", "zh-CN-YunjianNeural")
        final_speed = speed if speed is not None else local_config.get("speed", 1.2)

        # Chuyển speed sang tham số rate
        rate = speed_to_rate(final_speed)

        logger.info(f"🎙️  Đang dùng Edge TTS local: voice={final_voice}, speed={final_speed}x (rate={rate})")

        # Sinh đường dẫn output nếu chưa có
        if not output_path:
            # Sinh tên file duy nhất
            unique_id = uuid.uuid4().hex
            output_path = f"output/{unique_id}.mp3"

            # Đảm bảo thư mục output tồn tại
            Path("output").mkdir(parents=True, exist_ok=True)

        # Gọi Edge TTS
        try:
            audio_bytes = await edge_tts(
                text=text,
                voice=final_voice,
                rate=rate,
                output_path=output_path
            )

            logger.info(f"✅ Đã sinh audio (Edge TTS local): {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Lỗi sinh TTS local: {e}")
            raise
    
    async def _call_comfyui_workflow(
        self,
        workflow_info: dict,
        text: str,
        comfyui_url: Optional[str] = None,
        runninghub_api_key: Optional[str] = None,
        voice: Optional[str] = None,
        speed: float = 1.0,
        output_path: Optional[str] = None,
        **params
    ) -> str:
        """
        Sinh giọng nói dùng workflow ComfyUI

        Args:
            workflow_info: Dict thông tin workflow từ _resolve_workflow()
            text: Văn bản cần chuyển thành giọng nói
            comfyui_url: URL ComfyUI
            runninghub_api_key: API key RunningHub
            voice: ID giọng (theo workflow)
            speed: Hệ số tốc độ đọc (theo workflow)
            output_path: Đường dẫn output tuỳ chỉnh (tải xuống nếu trả về URL)
            **params: Tham số workflow bổ sung

        Returns:
            Đường dẫn file audio đã sinh (local nếu có output_path, ngược lại là URL)
        """
        logger.info(f"🎙️  Đang dùng workflow: {workflow_info['key']}")

        # 1. Xây dựng tham số workflow (cấu hình ComfyKit do core quản lý)
        workflow_params = {"text": text}

        # Thêm tham số TTS tuỳ chọn (chỉ khi được cung cấp rõ ràng và không None)
        if voice is not None:
            workflow_params["voice"] = voice
        if speed is not None and speed != 1.0:
            workflow_params["speed"] = speed

        # Thêm các tham số bổ sung
        workflow_params.update(params)

        logger.debug(f"Tham số workflow: {workflow_params}")

        # 3. Thực thi workflow dùng instance ComfyKit dùng chung từ core
        try:
            # Lấy instance ComfyKit dùng chung (khởi tạo lười + hot-reload config)
            kit = await self.core._get_or_create_comfykit()

            # Xác định truyền gì cho ComfyKit dựa trên source
            if workflow_info["source"] == "runninghub" and "workflow_id" in workflow_info:
                # RunningHub: truyền workflow_id
                workflow_input = workflow_info["workflow_id"]
                logger.info(f"Đang thực thi workflow TTS RunningHub: {workflow_input}")
            else:
                # Selfhost: truyền đường dẫn file
                workflow_input = workflow_info["path"]
                logger.info(f"Đang thực thi workflow TTS selfhost: {workflow_input}")

            result = await kit.execute(workflow_input, workflow_params)

            # 4. Xử lý kết quả
            if result.status != "completed":
                error_msg = result.msg or "Lỗi không xác định"
                logger.error(f"Sinh TTS thất bại: {error_msg}")
                raise Exception(f"Sinh TTS thất bại: {error_msg}")

            # Kết quả ComfyKit có thể có file audio ở các loại output khác nhau
            # Thử lấy đường dẫn file audio từ kết quả
            audio_path = None

            # Kiểm tra file audio trong result.audios (nếu có)
            if hasattr(result, 'audios') and result.audios:
                audio_path = result.audios[0]
                logger.debug(f"✅ Tìm thấy audio trong result.audios: {audio_path}")
            # Kiểm tra file trong result.files
            elif hasattr(result, 'files') and result.files:
                audio_path = result.files[0]
                logger.debug(f"✅ Tìm thấy audio trong result.files: {audio_path}")
            # Kiểm tra trong dictionary outputs
            elif hasattr(result, 'outputs') and result.outputs:
                logger.debug(f"Đang tìm file audio trong result.outputs: {result.outputs}")
                # Thử tìm file audio trong outputs
                for key, value in result.outputs.items():
                    if isinstance(value, str) and any(value.endswith(ext) for ext in ['.mp3', '.wav', '.flac']):
                        audio_path = value
                        logger.debug(f"✅ Tìm thấy audio trong result.outputs[{key}]: {audio_path}")
                        break

            if not audio_path:
                logger.error("Không sinh được file audio")
                logger.error(f"❌ Phân tích kết quả:")
                logger.error(f"   - result.audios: {getattr(result, 'audios', 'NOT_FOUND')}")
                logger.error(f"   - result.files: {getattr(result, 'files', 'NOT_FOUND')}")
                logger.error(f"   - result.outputs: {getattr(result, 'outputs', 'NOT_FOUND')}")
                logger.error(f"   - __dict__ đầy đủ: {result.__dict__}")
                raise Exception("Workflow không sinh được file audio")

            # Nếu có output_path và audio_path là URL, tải về local
            if output_path and audio_path.startswith(('http://', 'https://')):
                import httpx
                import os

                # Đảm bảo thư mục cha tồn tại
                os.makedirs(os.path.dirname(output_path), exist_ok=True)

                logger.info(f"Đang tải audio từ {audio_path} về {output_path}")
                async with httpx.AsyncClient() as client:
                    response = await client.get(audio_path)
                    response.raise_for_status()

                    with open(output_path, 'wb') as f:
                        f.write(response.content)

                logger.info(f"✅ Đã sinh audio (ComfyUI): {output_path}")
                return output_path

            logger.info(f"✅ Đã sinh audio (ComfyUI): {audio_path}")
            return audio_path

        except Exception as e:
            logger.error(f"Lỗi sinh TTS: {e}")
            raise
