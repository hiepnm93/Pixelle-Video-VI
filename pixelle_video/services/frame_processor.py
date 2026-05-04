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
Frame processor - Xử lý một frame đơn qua toàn bộ pipeline

Điều phối: TTS → Tạo Image → Compose Frame → Tạo Video Segment

Tính năng chính:
- Thời lượng video do TTS quyết định: Thời lượng audio từ TTS được truyền vào các workflow
  tạo video để đảm bảo audio và video đồng bộ hoàn hảo (không cần padding hay trim)
"""

from typing import Callable, Optional

import httpx
from loguru import logger

from pixelle_video.models.progress import ProgressEvent
from pixelle_video.models.storyboard import Storyboard, StoryboardFrame, StoryboardConfig


class FrameProcessor:
    """Frame processor"""

    def __init__(self, pixelle_video_core):
        """
        Khởi tạo

        Args:
            pixelle_video_core: Instance của PixelleVideoCore
        """
        self.core = pixelle_video_core
    
    async def __call__(
        self,
        frame: StoryboardFrame,
        storyboard: 'Storyboard',
        config: StoryboardConfig,
        total_frames: int = 1,
        progress_callback: Optional[Callable[[ProgressEvent], None]] = None
    ) -> StoryboardFrame:
        """
        Xử lý một frame đơn qua toàn bộ pipeline

        Các bước:
        1. Tạo audio (TTS)
        2. Tạo image (ComfyKit)
        3. Compose frame (thêm phụ đề)
        4. Tạo video segment (image + audio)

        Args:
            frame: Storyboard frame cần xử lý
            storyboard: Instance Storyboard
            config: Cấu hình Storyboard
            total_frames: Tổng số frame trong storyboard
            progress_callback: Callback tùy chọn cho cập nhật tiến độ (nhận ProgressEvent)

        Returns:
            Frame đã xử lý xong với đầy đủ các đường dẫn
        """
        logger.info(f"Đang xử lý frame {frame.index}...")

        frame_num = frame.index + 1

        # Xác định xem frame này có cần tạo ảnh hay không
        # Nếu image_path hoặc video_path đã được set sẵn (ví dụ pipeline dựa trên asset), ta coi là "đã có media sẵn" nhưng bỏ qua bước tạo
        has_existing_media = frame.image_path is not None or frame.video_path is not None
        needs_generation = frame.image_prompt is not None

        try:
            # Bước 1: Tạo audio (TTS)
            if not frame.audio_path:
                if progress_callback:
                    progress_callback(ProgressEvent(
                        event_type="frame_step",
                        progress=0.0,
                        frame_current=frame_num,
                        frame_total=total_frames,
                        step=1,
                        action="audio"
                    ))
                await self._step_generate_audio(frame, config)
            else:
                logger.debug(f"  1/4: Sử dụng audio có sẵn: {frame.audio_path}")

            # Bước 2: Tạo media (image hoặc video, có điều kiện)
            if needs_generation:
                if progress_callback:
                    progress_callback(ProgressEvent(
                        event_type="frame_step",
                        progress=0.25,
                        frame_current=frame_num,
                        frame_total=total_frames,
                        step=2,
                        action="media"
                    ))
                await self._step_generate_media(frame, config)
            elif has_existing_media:
                # Ghi log thông điệp tương ứng theo loại media
                if frame.video_path:
                    logger.debug(f"  2/4: Sử dụng video có sẵn: {frame.video_path}")
                else:
                    logger.debug(f"  2/4: Sử dụng image có sẵn: {frame.image_path}")
            else:
                frame.image_path = None
                frame.media_type = None
                logger.debug(f"  2/4: Đã bỏ qua tạo media (template không yêu cầu)")

            # Bước 3: Compose frame (thêm phụ đề)
            if progress_callback:
                progress_callback(ProgressEvent(
                    event_type="frame_step",
                    progress=0.50 if (needs_generation or has_existing_media) else 0.33,
                    frame_current=frame_num,
                    frame_total=total_frames,
                    step=3,
                    action="compose"
                ))
            await self._step_compose_frame(frame, storyboard, config)

            # Bước 4: Tạo video segment
            if progress_callback:
                progress_callback(ProgressEvent(
                    event_type="frame_step",
                    progress=0.75 if (needs_generation or has_existing_media) else 0.67,
                    frame_current=frame_num,
                    frame_total=total_frames,
                    step=4,
                    action="video"
                ))
            
            await self._step_create_video_segment(frame, config)

            logger.info(f"✅ Hoàn tất frame {frame.index}")
            return frame

        except Exception as e:
            logger.error(f"❌ Xử lý frame {frame.index} thất bại: {e}")
            raise
    
    async def _step_generate_audio(
        self,
        frame: StoryboardFrame,
        config: StoryboardConfig
    ):
        """Bước 1: Tạo audio bằng TTS"""
        logger.debug(f"  1/4: Đang tạo audio cho frame {frame.index}...")

        # Tạo đường dẫn output dùng task_id
        from pixelle_video.utils.os_util import get_task_frame_path
        output_path = get_task_frame_path(config.task_id, frame.index, "audio")

        # Xây dựng tham số TTS dựa trên inference mode
        tts_params = {
            "text": frame.narration,
            "inference_mode": config.tts_inference_mode,
            "output_path": output_path,
            "index": frame.index + 1,  # Index 1-based cho workflow
        }

        if config.tts_inference_mode == "local":
            # Chế độ local: truyền voice và speed
            if config.voice_id:
                tts_params["voice"] = config.voice_id
            if config.tts_speed is not None:
                tts_params["speed"] = config.tts_speed
        else:  # comfyui
            # Chế độ ComfyUI: truyền workflow, voice, speed, và ref_audio
            if config.tts_workflow:
                tts_params["workflow"] = config.tts_workflow
            if config.voice_id:
                tts_params["voice"] = config.voice_id
            if config.tts_speed is not None:
                tts_params["speed"] = config.tts_speed
            if config.ref_audio:
                tts_params["ref_audio"] = config.ref_audio

        audio_path = await self.core.tts(**tts_params)

        frame.audio_path = audio_path

        # Lấy thời lượng audio
        frame.duration = await self._get_audio_duration(audio_path)

        logger.debug(f"  ✓ Đã tạo audio: {audio_path} ({frame.duration:.2f}s)")
    
    async def _step_generate_media(
        self,
        frame: StoryboardFrame,
        config: StoryboardConfig
    ):
        """Bước 2: Tạo media (image hoặc video) bằng ComfyKit"""
        logger.debug(f"  2/4: Đang tạo media cho frame {frame.index}...")

        # Xác định loại media dựa trên workflow
        # Tiền tố video_ trong tên workflow cho biết sẽ tạo video
        workflow_name = config.media_workflow or ""
        is_video_workflow = "video_" in workflow_name.lower()
        media_type = "video" if is_video_workflow else "image"

        logger.debug(f"  → Loại media: {media_type} (workflow: {workflow_name})")

        # Xây dựng tham số tạo media
        media_params = {
            "prompt": frame.image_prompt,
            "workflow": config.media_workflow,  # Truyền workflow từ config (None = dùng mặc định)
            "media_type": media_type,
            "width": config.media_width,
            "height": config.media_height,
            "index": frame.index + 1,  # Index 1-based cho workflow
        }

        # Với workflow video: truyền thời lượng audio làm thời lượng video mục tiêu
        # Điều này đảm bảo độ dài video khớp với độ dài audio nguồn
        if is_video_workflow and frame.duration:
            media_params["duration"] = frame.duration
            logger.info(f"  → Đang tạo video với thời lượng mục tiêu: {frame.duration:.2f}s (từ TTS audio)")

        # Gọi tạo Media
        media_result = await self.core.media(**media_params)

        # Lưu loại media
        frame.media_type = media_result.media_type

        if media_result.is_image:
            # Tải ảnh về local (truyền task_id)
            local_path = await self._download_media(
                media_result.url,
                frame.index,
                config.task_id,
                media_type="image"
            )
            frame.image_path = local_path
            logger.debug(f"  ✓ Đã tạo image: {local_path}")

        elif media_result.is_video:
            # Tải video về local (truyền task_id)
            local_path = await self._download_media(
                media_result.url,
                frame.index,
                config.task_id,
                media_type="video"
            )
            frame.video_path = local_path

            # Cập nhật thời lượng từ video nếu có
            if media_result.duration:
                frame.duration = media_result.duration
                logger.debug(f"  ✓ Đã tạo video: {local_path} (thời lượng: {frame.duration:.2f}s)")
            else:
                # Lấy thời lượng video từ file
                frame.duration = await self._get_video_duration(local_path)
                logger.debug(f"  ✓ Đã tạo video: {local_path} (thời lượng: {frame.duration:.2f}s)")

        else:
            raise ValueError(f"Loại media không xác định: {media_result.media_type}")
    
    async def _step_compose_frame(
        self,
        frame: StoryboardFrame,
        storyboard: 'Storyboard',
        config: StoryboardConfig
    ):
        """Bước 3: Compose frame có phụ đề bằng template HTML"""
        logger.debug(f"  3/4: Đang compose frame {frame.index}...")

        # Tạo đường dẫn output dùng task_id
        from pixelle_video.utils.os_util import get_task_frame_path
        output_path = get_task_frame_path(config.task_id, frame.index, "composed")

        # Với loại video: render HTML thành ảnh overlay trong suốt
        # Với loại image: render HTML có ảnh nền
        # Cả hai trường hợp đều cần ảnh đã compose
        composed_path = await self._compose_frame_html(frame, storyboard, config, output_path)

        frame.composed_image_path = composed_path

        logger.debug(f"  ✓ Đã compose frame: {composed_path}")
    
    async def _compose_frame_html(
        self,
        frame: StoryboardFrame,
        storyboard: 'Storyboard',
        config: StoryboardConfig,
        output_path: str
    ) -> str:
        """Compose frame bằng template HTML"""
        from pixelle_video.services.frame_html import HTMLFrameGenerator
        from pixelle_video.utils.template_util import resolve_template_path

        # Resolve đường dẫn template (xử lý nhiều dạng input khác nhau)
        template_path = resolve_template_path(config.frame_template)

        # Lấy metadata nội dung từ storyboard
        content_metadata = storyboard.content_metadata if storyboard else None

        # Xây dựng dữ liệu ext
        ext = {
            "index": frame.index + 1,
        }

        # Thêm các tham số tùy chỉnh của template
        if config.template_params:
            ext.update(config.template_params)

        # Tạo frame bằng HTML (kích thước được tự động lấy từ đường dẫn template)
        generator = HTMLFrameGenerator(template_path)

        # Dùng video_path với media là video, image_path với image
        media_path = frame.video_path if frame.media_type == "video" else frame.image_path
        logger.debug(f"Đang tạo frame với media: '{media_path}' (loại: {frame.media_type})")
        
        composed_path = await generator.generate_frame(
            title=storyboard.title,
            text=frame.narration,
            image=media_path,  # HTMLFrameGenerator xử lý cả đường dẫn image lẫn video
            ext=ext,
            output_path=output_path
        )
        
        return composed_path
    
    async def _step_create_video_segment(
        self,
        frame: StoryboardFrame,
        config: StoryboardConfig
    ):
        """Bước 4: Tạo video segment từ media + audio"""
        logger.debug(f"  4/4: Đang tạo video segment cho frame {frame.index}...")

        # Tạo đường dẫn output dùng task_id
        from pixelle_video.utils.os_util import get_task_frame_path
        output_path = get_task_frame_path(config.task_id, frame.index, "segment")

        from pixelle_video.services.video import VideoService
        video_service = VideoService()

        # Phân nhánh theo loại media
        if frame.media_type == "video":
            # Workflow video: overlay template HTML lên video, rồi thêm audio
            logger.debug(f"  → Sử dụng compose dựa trên video với overlay HTML")

            # Bước 1: Overlay ảnh HTML trong suốt lên video
            # composed_image_path chứa HTML đã render với nền trong suốt
            temp_video_with_overlay = get_task_frame_path(config.task_id, frame.index, "video") + "_overlay.mp4"

            video_service.overlay_image_on_video(
                video=frame.video_path,
                overlay_image=frame.composed_image_path,
                output=temp_video_with_overlay,
                scale_mode="contain"  # Scale video vừa kích thước template (chế độ contain)
            )

            # Bước 2: Thêm audio thuyết minh vào video đã overlay
            # Lưu ý: Video có thể có audio (sẽ thay thế) hoặc không có (sẽ thêm vào)
            segment_path = video_service.merge_audio_video(
                video=temp_video_with_overlay,
                audio=frame.audio_path,
                output=output_path,
                replace_audio=True,  # Thay audio của video bằng audio thuyết minh
                audio_volume=1.0
            )

            # Dọn dẹp file tạm
            import os
            if os.path.exists(temp_video_with_overlay):
                os.unlink(temp_video_with_overlay)

        elif frame.media_type == "image" or frame.media_type is None:
            # Workflow image: dùng trực tiếp ảnh đã compose
            # Template asset_default.html đã bao gồm ảnh trong khung compose
            logger.debug(f"  → Sử dụng compose dựa trên image")

            segment_path = video_service.create_video_from_image(
                image=frame.composed_image_path,
                audio=frame.audio_path,
                output=output_path,
                fps=config.video_fps
            )

        else:
            raise ValueError(f"Loại media không xác định: {frame.media_type}")

        frame.video_segment_path = segment_path

        logger.debug(f"  ✓ Đã tạo video segment: {segment_path}")
    
    async def _get_audio_duration(self, audio_path: str) -> float:
        """Lấy thời lượng audio tính bằng giây"""
        try:
            # Thử dùng ffmpeg-python
            import ffmpeg
            probe = ffmpeg.probe(audio_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.warning(f"Không lấy được thời lượng audio: {e}, đang ước lượng")
            # Phương án dự phòng: ước lượng theo kích thước file (rất thô)
            import os
            file_size = os.path.getsize(audio_path)
            # Giả định ~16kbps cho MP3, tức ~2KB mỗi giây
            estimated_duration = file_size / 2000
            return max(1.0, estimated_duration)  # Tối thiểu 1 giây
    
    async def _download_media(
        self,
        url: str,
        frame_index: int,
        task_id: str,
        media_type: str
    ) -> str:
        """Tải media (image hoặc video) từ URL về file local"""
        from pixelle_video.utils.os_util import get_task_frame_path
        output_path = get_task_frame_path(task_id, frame_index, media_type)
        
        timeout = httpx.Timeout(connect=10.0, read=60, write=60, pool=60)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
        
        return output_path
    
    async def _get_video_duration(self, video_path: str) -> float:
        """Lấy thời lượng video tính bằng giây"""
        try:
            import ffmpeg
            probe = ffmpeg.probe(video_path)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.warning(f"Không lấy được thời lượng video: {e}, sử dụng thời lượng audio")
            # Phương án dự phòng: dùng thời lượng audio nếu có
            return 1.0  # Mặc định 1 giây nếu không xác định được

