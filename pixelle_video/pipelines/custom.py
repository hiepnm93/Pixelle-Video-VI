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
Pipeline tạo video tuỳ chỉnh

Pipeline mẫu để tạo các workflow tạo video tuỳ chỉnh của riêng bạn.
Đây là một implementation tham chiếu cho thấy cách mở rộng BasePipeline.

Với project thực tế, hãy copy file này và sửa đổi theo nhu cầu.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Callable

from loguru import logger

from pixelle_video.pipelines.base import BasePipeline
from pixelle_video.models.progress import ProgressEvent
from pixelle_video.models.storyboard import (
    Storyboard,
    StoryboardFrame,
    StoryboardConfig,
    ContentMetadata,
    VideoGenerationResult
)


class CustomPipeline(BasePipeline):
    """
    Mẫu pipeline tạo video tuỳ chỉnh

    Đây là mẫu cho thấy cách tạo pipeline với logic tuỳ chỉnh của riêng bạn.
    Bạn có thể tuỳ biến:
    - Logic xử lý nội dung
    - Chiến lược sinh thuyết minh
    - Sinh prompt ảnh (có điều kiện dựa trên template)
    - Ghép frame
    - Lắp ráp video

    TỐI ƯU CHÍNH: Sinh ảnh có điều kiện
    -----------------------------------------------
    Pipeline này hỗ trợ tự động phát hiện yêu cầu ảnh của template.
    Nếu template của bạn không dùng {{image}}, toàn bộ pipeline sinh ảnh
    có thể bỏ qua, mang lại:
      ⚡ Tạo nhanh hơn (không gọi API tạo ảnh)
      💰 Chi phí thấp hơn (không gọi LLM để sinh prompt ảnh)
      🚀 Giảm phụ thuộc (không cần ComfyUI cho video chỉ có text)

    Mẫu sử dụng:
      1. Video chỉ có text: Dùng templates/1080x1920/simple.html
      2. Ảnh sinh bằng AI: Dùng template có placeholder {{image}}
      3. Logic tuỳ chỉnh: Sửa template hoặc override logic phát hiện trong subclass của bạn

    Ví dụ sử dụng:
        # 1. Tạo pipeline của riêng bạn bằng cách copy file này
        # 2. Sửa method __call__ với logic tuỳ chỉnh của bạn
        # 3. Đăng ký nó trong service.py hoặc động

        from pixelle_video.pipelines.custom import CustomPipeline
        pixelle_video.pipelines["my_custom"] = CustomPipeline(pixelle_video)

        # 4. Sử dụng
        result = await pixelle_video.generate_video(
            text=your_content,
            pipeline="my_custom",
            # Tham số tuỳ chỉnh của bạn ở đây
        )
    """
    
    async def __call__(
        self,
        text: str,
        # === Tham số tuỳ chỉnh ===
        # Thêm tham số riêng của bạn ở đây
        custom_param_example: str = "default_value",

        # === Tham số tiêu chuẩn (giữ để tương thích) ===
        tts_inference_mode: Optional[str] = None,  # "local" hoặc "comfyui"
        voice_id: Optional[str] = None,  # Deprecated, dùng tts_voice
        tts_voice: Optional[str] = None,  # Voice ID cho chế độ local
        tts_workflow: Optional[str] = None,
        tts_speed: float = 1.2,
        ref_audio: Optional[str] = None,

        media_workflow: Optional[str] = None,
        # Lưu ý: media_width và media_height được tự động xác định từ template

        frame_template: Optional[str] = None,
        video_fps: int = 30,
        output_path: Optional[str] = None,

        bgm_path: Optional[str] = None,
        bgm_volume: float = 0.2,

        progress_callback: Optional[Callable[[ProgressEvent], None]] = None,
    ) -> VideoGenerationResult:
        """
        Workflow tạo video tuỳ chỉnh

        Tuỳ chỉnh method này để implement logic của riêng bạn.

        Args:
            text: Văn bản đầu vào (tuỳ chỉnh ý nghĩa theo nhu cầu)
            custom_param_example: Tham số tuỳ chỉnh của bạn
            (các tham số tiêu chuẩn khác...)

        Returns:
            VideoGenerationResult

        Logic sinh ảnh:
            - Template image_*.html → tự động sinh ảnh
            - Template video_*.html → tự động sinh video
            - Template static_*.html → bỏ qua sinh media (nhanh hơn, rẻ hơn)
            - Để tuỳ chỉnh: Override logic phát hiện loại template trong subclass của bạn
        """
        logger.info("Bắt đầu CustomPipeline")
        logger.info(f"Độ dài văn bản đầu vào: {len(text)} ký tự")
        logger.info(f"Tham số tuỳ chỉnh: {custom_param_example}")

        # === Xử lý tương thích tham số TTS ===
        # Hỗ trợ cả API cũ (voice_id) và API mới (tts_inference_mode + tts_voice)
        final_voice_id = None
        final_tts_workflow = tts_workflow

        if tts_inference_mode:
            # API mới từ web UI
            if tts_inference_mode == "local":
                # Chế độ Edge TTS local - dùng tts_voice
                final_voice_id = tts_voice or "zh-CN-YunjianNeural"
                final_tts_workflow = None  # Không dùng workflow ở chế độ local
                logger.debug(f"Chế độ TTS: local (voice={final_voice_id})")
            elif tts_inference_mode == "comfyui":
                # Chế độ workflow ComfyUI
                final_voice_id = None  # Không dùng voice_id ở chế độ ComfyUI
                # tts_workflow đã được đặt từ tham số
                logger.debug(f"Chế độ TTS: comfyui (workflow={final_tts_workflow})")
        else:
            # API cũ (giữ tương thích ngược)
            final_voice_id = voice_id or tts_voice or "zh-CN-YunjianNeural"
            # tts_workflow đã được đặt từ tham số
            logger.debug(f"Chế độ TTS: legacy (voice_id={final_voice_id}, workflow={final_tts_workflow})")

        # ========== Bước 0: Setup ==========
        self._report_progress(progress_callback, "initializing", 0.05)

        # Tạo thư mục cho task
        from pixelle_video.utils.os_util import (
            create_task_output_dir,
            get_task_final_video_path
        )

        task_dir, task_id = create_task_output_dir()
        logger.info(f"Thư mục task: {task_dir}")
        
        user_specified_output = None
        if output_path is None:
            output_path = get_task_final_video_path(task_id)
        else:
            user_specified_output = output_path
            output_path = get_task_final_video_path(task_id)
        
        # Xác định template frame
        # Ưu tiên: tham số rõ ràng > mặc định trong config > mặc định hardcode
        if frame_template is None:
            template_config = self.core.config.get("template", {})
            frame_template = template_config.get("default_template", "1080x1920/default.html")

        # ========== Bước 0.5: Kiểm tra yêu cầu của template ==========
        # Phát hiện loại template theo tiền tố tên file
        from pathlib import Path
        from pixelle_video.services.frame_html import HTMLFrameGenerator
        from pixelle_video.utils.template_util import resolve_template_path, get_template_type

        template_name = Path(frame_template).name
        template_type = get_template_type(template_name)
        template_requires_image = (template_type == "image")

        # Đọc kích thước media từ meta tag của template
        template_path = resolve_template_path(frame_template)
        generator = HTMLFrameGenerator(template_path)
        media_width, media_height = generator.get_media_size()
        logger.info(f"📐 Kích thước media từ template: {media_width}x{media_height}")

        if template_type == "image":
            logger.info(f"📸 Template yêu cầu sinh ảnh")
        elif template_type == "video":
            logger.info(f"🎬 Template yêu cầu sinh video")
        else:  # static
            logger.info(f"⚡ Template tĩnh - bỏ qua pipeline sinh media")
            logger.info(f"   💡 Lợi ích: Tạo nhanh hơn + Chi phí thấp hơn + Không phụ thuộc ComfyUI")

        # ========== Bước 1: Xử lý nội dung (TUỲ CHỈNH PHẦN NÀY) ==========
        self._report_progress(progress_callback, "processing_content", 0.10)

        # Ví dụ: Sinh tiêu đề bằng LLM
        from pixelle_video.utils.content_generators import generate_title
        title = await generate_title(self.llm, text, strategy="llm")
        logger.info(f"Tiêu đề đã sinh: '{title}'")

        # Ví dụ: Tách hoặc sinh thuyết minh
        # Lựa chọn A: Tách theo dòng (cho kịch bản cố định)
        narrations = [line.strip() for line in text.split('\n') if line.strip()]

        # Lựa chọn B: Dùng LLM để sinh thuyết minh (bỏ comment để dùng)
        # from pixelle_video.utils.content_generators import generate_narrations_from_topic
        # narrations = await generate_narrations_from_topic(
        #     self.llm,
        #     topic=text,
        #     n_scenes=5,
        #     min_words=20,
        #     max_words=80
        # )

        logger.info(f"Đã sinh {len(narrations)} thuyết minh")

        # ========== Bước 2: Sinh prompt ảnh (CÓ ĐIỀU KIỆN - TUỲ CHỈNH PHẦN NÀY) ==========
        self._report_progress(progress_callback, "generating_image_prompts", 0.25)

        # QUAN TRỌNG: Kiểm tra template có phải loại image không
        # Nếu template là static_*.html, bạn có thể bỏ qua toàn bộ bước này!
        if template_requires_image:
            # Template yêu cầu ảnh - sinh prompt ảnh dùng LLM
            from pixelle_video.utils.content_generators import generate_image_prompts

            image_prompts = await generate_image_prompts(
                self.llm,
                narrations=narrations,
                min_words=30,
                max_words=60
            )

            # Ví dụ: Áp dụng tiền tố prompt tuỳ chỉnh
            from pixelle_video.utils.prompt_helper import build_image_prompt
            custom_prefix = "cinematic style, professional lighting"  # Tuỳ chỉnh phần này

            final_image_prompts = []
            for base_prompt in image_prompts:
                final_prompt = build_image_prompt(base_prompt, custom_prefix)
                final_image_prompts.append(final_prompt)

            logger.info(f"✅ Đã sinh {len(final_image_prompts)} prompt ảnh")
        else:
            # Template không cần ảnh - bỏ qua toàn bộ phần sinh ảnh
            final_image_prompts = [None] * len(narrations)
            logger.info(f"⚡ Bỏ qua sinh prompt ảnh (template không cần ảnh)")
            logger.info(f"   💡 Tiết kiệm: {len(narrations)} lệnh gọi LLM + {len(narrations)} lần sinh ảnh")
        
        # ========== Bước 3: Tạo storyboard ==========
        config = StoryboardConfig(
            task_id=task_id,
            n_storyboard=len(narrations),
            min_narration_words=20,
            max_narration_words=80,
            min_image_prompt_words=30,
            max_image_prompt_words=60,
            video_fps=video_fps,
            tts_inference_mode=tts_inference_mode or "local",  # Chế độ inference TTS (FIX QUAN TRỌNG)
            voice_id=final_voice_id,  # Dùng voice_id đã xử lý
            tts_workflow=final_tts_workflow,  # Dùng workflow đã xử lý
            tts_speed=tts_speed,
            ref_audio=ref_audio,
            media_width=media_width,
            media_height=media_height,
            media_workflow=media_workflow,
            frame_template=frame_template
        )
        
        # Tuỳ chọn: Thêm metadata tuỳ chỉnh
        content_metadata = ContentMetadata(
            title=title,
            subtitle="Output từ Custom Pipeline"
        )
        
        storyboard = Storyboard(
            title=title,
            config=config,
            content_metadata=content_metadata,
            created_at=datetime.now()
        )
        
        # Tạo các frame
        for i, (narration, image_prompt) in enumerate(zip(narrations, final_image_prompts)):
            frame = StoryboardFrame(
                index=i,
                narration=narration,
                image_prompt=image_prompt,
                created_at=datetime.now()
            )
            storyboard.frames.append(frame)

        try:
            # ========== Bước 4: Xử lý từng frame ==========
            # Đây là logic xử lý frame tiêu chuẩn
            # Bạn có thể tuỳ chỉnh xử lý frame nếu cần

            for i, frame in enumerate(storyboard.frames):
                base_progress = 0.3
                frame_range = 0.5
                per_frame_progress = frame_range / len(storyboard.frames)
                
                self._report_progress(
                    progress_callback,
                    "processing_frame",
                    base_progress + (per_frame_progress * i),
                    frame_current=i+1,
                    frame_total=len(storyboard.frames)
                )
                
                # Dùng frame processor của core (logic tiêu chuẩn)
                processed_frame = await self.core.frame_processor(
                    frame=frame,
                    storyboard=storyboard,
                    config=config,
                    total_frames=len(storyboard.frames),
                    progress_callback=None
                )
                storyboard.total_duration += processed_frame.duration
                logger.info(f"Frame {i+1} hoàn thành ({processed_frame.duration:.2f}s)")

            # ========== Bước 5: Ghép các video ==========
            self._report_progress(progress_callback, "concatenating", 0.85)
            segment_paths = [frame.video_segment_path for frame in storyboard.frames]
            
            from pixelle_video.services.video import VideoService
            video_service = VideoService()
            
            final_video_path = video_service.concat_videos(
                videos=segment_paths,
                output=output_path,
                bgm_path=bgm_path,
                bgm_volume=bgm_volume,
                bgm_mode="loop"
            )
            
            storyboard.final_video_path = final_video_path
            storyboard.completed_at = datetime.now()
            
            # Copy tới đường dẫn người dùng chỉ định nếu có
            if user_specified_output:
                import shutil
                Path(user_specified_output).parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(final_video_path, user_specified_output)
                logger.info(f"Đã copy video cuối tới: {user_specified_output}")
                final_video_path = user_specified_output
                storyboard.final_video_path = user_specified_output

            logger.success(f"Video custom pipeline hoàn thành: {final_video_path}")

            # ========== Bước 6: Tạo kết quả ==========
            self._report_progress(progress_callback, "completed", 1.0)

            video_path_obj = Path(final_video_path)
            file_size = video_path_obj.stat().st_size

            result = VideoGenerationResult(
                video_path=final_video_path,
                storyboard=storyboard,
                duration=storyboard.total_duration,
                file_size=file_size
            )

            logger.info(f"Custom pipeline hoàn thành")
            logger.info(f"Tiêu đề: {title}")
            logger.info(f"Thời lượng: {storyboard.total_duration:.2f}s")
            logger.info(f"Kích thước: {file_size / (1024*1024):.2f} MB")
            logger.info(f"Số frame: {len(storyboard.frames)}")

            # ========== Bước 7: Lưu metadata và storyboard ==========
            await self._persist_task_data(
                storyboard=storyboard,
                result=result,
                input_params={
                    "text": text,
                    "custom_param_example": custom_param_example,
                    "voice_id": voice_id,
                    "tts_workflow": tts_workflow,
                    "tts_speed": tts_speed,
                    "ref_audio": ref_audio,
                    "media_workflow": media_workflow,
                    "frame_template": frame_template,
                    "bgm_path": bgm_path,
                    "bgm_volume": bgm_volume,
                }
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Custom pipeline thất bại: {e}")
            raise

    # ==================== Persistence ====================

    async def _persist_task_data(
        self,
        storyboard: Storyboard,
        result: VideoGenerationResult,
        input_params: dict
    ):
        """
        Lưu metadata task và storyboard vào filesystem

        Args:
            storyboard: Storyboard hoàn chỉnh
            result: Kết quả tạo video
            input_params: Tham số đầu vào dùng để tạo
        """
        try:
            task_id = storyboard.config.task_id
            if not task_id:
                logger.warning("Không có task_id trong storyboard, bỏ qua persistence")
                return

            # Xây dựng metadata
            # Nếu user không cung cấp tiêu đề, dùng tiêu đề đã sinh từ storyboard
            input_with_title = input_params.copy()
            if not input_with_title.get("title"):
                input_with_title["title"] = storyboard.title
            
            metadata = {
                "task_id": task_id,
                "created_at": storyboard.created_at.isoformat() if storyboard.created_at else None,
                "completed_at": storyboard.completed_at.isoformat() if storyboard.completed_at else None,
                "status": "completed",
                
                "input": input_with_title,
                
                "result": {
                    "video_path": result.video_path,
                    "duration": result.duration,
                    "file_size": result.file_size,
                    "n_frames": len(storyboard.frames)
                },
                
                "config": {
                    "llm_model": self.core.config.get("llm", {}).get("model", "unknown"),
                    "llm_base_url": self.core.config.get("llm", {}).get("base_url", "unknown"),
                    "comfyui_url": self.core.config.get("comfyui", {}).get("comfyui_url", "unknown"),
                    "runninghub_enabled": bool(self.core.config.get("comfyui", {}).get("runninghub_api_key")),
                }
            }
            
            # Lưu metadata
            await self.core.persistence.save_task_metadata(task_id, metadata)
            logger.info(f"💾 Đã lưu metadata task: {task_id}")

            # Lưu storyboard
            await self.core.persistence.save_storyboard(task_id, storyboard)
            logger.info(f"💾 Đã lưu storyboard: {task_id}")

        except Exception as e:
            logger.error(f"Không thể lưu dữ liệu task: {e}")
            # Đừng raise - việc lưu thất bại không nên làm hỏng quá trình tạo video

    # ==================== Các method helper tuỳ chỉnh ====================
    # Thêm các method helper riêng của bạn ở đây

    async def _custom_content_analysis(self, text: str) -> dict:
        """
        Ví dụ: Logic phân tích nội dung tuỳ chỉnh

        Bạn có thể thêm các method helper riêng để xử lý nội dung,
        trích xuất metadata, hoặc thực hiện các biến đổi tuỳ chỉnh.
        """
        # Logic tuỳ chỉnh của bạn ở đây
        return {
            "processed": text,
            "metadata": {}
        }

    async def _custom_prompt_generation(self, context: str) -> str:
        """
        Ví dụ: Logic sinh prompt tuỳ chỉnh

        Tạo các prompt chuyên biệt dựa trên use case của bạn.
        """
        prompt = f"Sinh nội dung dựa trên: {context}"
        response = await self.llm(prompt, temperature=0.7, max_tokens=500)
        return response.strip()


# ==================== Ví dụ sử dụng ====================

"""
Ví dụ 1: Video chỉ có text (không sinh ảnh bằng AI)
---------------------------------------------------
from pixelle_video import pixelle_video
from pixelle_video.pipelines.custom import CustomPipeline

# Initialize
await pixelle_video.initialize()

# Register custom pipeline
pixelle_video.pipelines["my_custom"] = CustomPipeline(pixelle_video)

# Use text-only template - no image generation!
result = await pixelle_video.generate_video(
    text="Your content here",
    pipeline="my_custom",
    frame_template="1080x1920/simple.html"  # Template without {{image}}
)
# Benefits: ⚡ Fast, 💰 Cheap, 🚀 No ComfyUI needed


Example 2: AI-generated image video
---------------------------------------------------
# Use template with {{image}} - automatic image generation
result = await pixelle_video.generate_video(
    text="Your content here",
    pipeline="my_custom",
    frame_template="1080x1920/default.html"  # Template with {{image}}
)
# Will automatically generate images via LLM + ComfyUI


Example 3: Create your own pipeline class
----------------------------------------
from pixelle_video.pipelines.custom import CustomPipeline

class MySpecialPipeline(CustomPipeline):
    async def __call__(self, text: str, **kwargs):
        # Your completely custom logic
        logger.info("Running my special pipeline")
        
        # You can reuse parts from CustomPipeline or start from scratch
        # ...
        
        return result


Example 4: Inline custom pipeline
----------------------------------------
from pixelle_video.pipelines.base import BasePipeline

class QuickPipeline(BasePipeline):
    async def __call__(self, text: str, **kwargs):
        # Quick custom logic
        narrations = text.split('\\n')
        
        for narration in narrations:
            audio = await self.tts(narration)
            image = await self.image(prompt=f"illustration of {narration}")
            # ... process frame
        
        # ... concatenate and return
        return result

# Use immediately
pixelle_video.pipelines["quick"] = QuickPipeline(pixelle_video)
result = await pixelle_video.generate_video(text=content, pipeline="quick")
"""

