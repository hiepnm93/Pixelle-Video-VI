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
Pipeline video dựa trên Asset

Tạo video marketing từ các asset do người dùng cung cấp (ảnh/video) thay vì
media được sinh bởi AI. Lý tưởng cho doanh nghiệp nhỏ có sẵn thư viện media.

Workflow:
1. Phân tích asset đã upload (ảnh/video)
2. Sinh kịch bản dựa trên ý định của người dùng và asset có sẵn
3. Khớp asset với các cảnh trong kịch bản
4. Ghép video cuối cùng với thuyết minh

Ví dụ:
    pipeline = AssetBasedPipeline(pixelle_video)
    result = await pipeline(
        assets=["/path/img1.jpg", "/path/img2.jpg"],
        video_title="Khuyến mãi cuối năm Cửa hàng Thú cưng",
        intent="Quảng bá khuyến mãi cuối năm của cửa hàng thú cưng với giọng điệu ấm áp và thân thiện",
        duration=30
    )
"""

from typing import List, Dict, Any, Optional, Callable
from pathlib import Path

from loguru import logger
from pydantic import BaseModel, Field

from pixelle_video.pipelines.linear import LinearVideoPipeline, PipelineContext
from pixelle_video.models.progress import ProgressEvent
from pixelle_video.utils.os_util import (
    create_task_output_dir,
    get_task_final_video_path
)

# Type alias cho callback tiến độ
ProgressCallback = Optional[Callable[[ProgressEvent], None]]


# ==================== Các model output có cấu trúc ====================

class SceneScript(BaseModel):
    """Một cảnh trong kịch bản video"""
    scene_number: int = Field(description="Số thứ tự cảnh, bắt đầu từ 1")
    asset_path: str = Field(description="Đường dẫn đến file asset cho cảnh này")
    narrations: List[str] = Field(description="Danh sách câu thuyết minh cho cảnh này (1-5 câu)")
    duration: int = Field(description="Thời lượng ước tính tính bằng giây cho cảnh này")


class VideoScript(BaseModel):
    """Kịch bản video hoàn chỉnh kèm các cảnh"""
    scenes: List[SceneScript] = Field(description="Danh sách các cảnh trong video")


class AssetBasedPipeline(LinearVideoPipeline):
    """
    Pipeline video dựa trên Asset

    Tạo video từ asset do người dùng cung cấp thay vì media do AI sinh.
    """

    def __init__(self, core):
        """
        Khởi tạo pipeline

        Args:
            core: Instance PixelleVideoCore
        """
        super().__init__(core)
        self.asset_index: Dict[str, Any] = {}  # Metadata asset trong bộ nhớ
    
    async def __call__(
        self,
        assets: List[str],
        video_title: str = "",
        intent: Optional[str] = None,
        duration: int = 30,
        source: str = "runninghub",
        bgm_path: Optional[str] = None,
        bgm_volume: float = 0.2,
        bgm_mode: str = "loop",
        progress_callback: ProgressCallback = None,
        **kwargs
    ) -> PipelineContext:
        """
        Thực thi pipeline với asset do người dùng cung cấp

        Args:
            assets: Danh sách đường dẫn file asset
            video_title: Tiêu đề video
            intent: Ý định/mục đích video (mặc định là video_title)
            duration: Thời lượng mục tiêu tính bằng giây
            source: Nguồn workflow ("runninghub" hoặc "selfhost")
            bgm_path: Đường dẫn file nhạc nền (tuỳ chọn)
            bgm_volume: Âm lượng BGM (0.0-1.0, mặc định 0.2)
            bgm_mode: Chế độ BGM ("loop" hoặc "once", mặc định "loop")
            progress_callback: Callback tuỳ chọn cho cập nhật tiến độ
            **kwargs: Tham số bổ sung

        Returns:
            Context pipeline với video đã sinh
        """
        from pixelle_video.pipelines.linear import PipelineContext

        # Lưu progress callback
        self._progress_callback = progress_callback

        # Tạo context tuỳ chỉnh với các tham số riêng cho asset
        ctx = PipelineContext(
            input_text=intent or video_title,  # Dùng intent hoặc tiêu đề làm input_text
            params={
                "assets": assets,
                "video_title": video_title,
                "intent": intent or video_title,
                "duration": duration,
                "source": source,
                "bgm_path": bgm_path,
                "bgm_volume": bgm_volume,
                "bgm_mode": bgm_mode,
                **kwargs
            }
        )
        
        # Lưu các tham số request vào context để truy cập dễ dàng
        ctx.request = ctx.params

        try:
            # Thực thi vòng đời pipeline
            await self.setup_environment(ctx)
            await self.determine_title(ctx)
            await self.generate_content(ctx)
            await self.plan_visuals(ctx)
            await self.initialize_storyboard(ctx)
            await self.produce_assets(ctx)
            await self.post_production(ctx)
            await self.finalize(ctx)
            
            return ctx
            
        except Exception as e:
            await self.handle_exception(ctx, e)
            raise
    
    def _emit_progress(self, event: ProgressEvent):
        """Phát sự kiện tiến độ tới callback nếu có"""
        if self._progress_callback:
            self._progress_callback(event)

    async def setup_environment(self, context: PipelineContext) -> PipelineContext:
        """
        Phân tích các asset đã upload và xây dựng asset index

        Args:
            context: Context pipeline kèm danh sách asset

        Returns:
            Context đã cập nhật với asset_index
        """
        # Tạo thư mục task cô lập
        task_dir, task_id = create_task_output_dir()
        context.task_id = task_id
        context.task_dir = Path(task_dir)  # Chuyển sang Path để dễ sử dụng

        # Xác định đường dẫn video cuối cùng
        context.final_video_path = get_task_final_video_path(task_id)

        logger.info(f"📁 Đã tạo thư mục task: {task_dir}")
        logger.info("🔍 Đang phân tích asset đã upload...")

        assets: List[str] = context.request.get("assets", [])
        if not assets:
            raise ValueError("Không có asset nào được cung cấp. Vui lòng upload ít nhất một ảnh hoặc video.")

        total_assets = len(assets)
        logger.info(f"Tìm thấy {total_assets} asset cần phân tích")
        
        # Emit initial progress (0-15% for asset analysis)
        self._emit_progress(ProgressEvent(
            event_type="analyzing_assets",
            progress=0.01,
            frame_current=0,
            frame_total=total_assets,
            extra_info="start"
        ))
        
        self.asset_index = {}
        
        for i, asset_path in enumerate(assets, 1):
            asset_path_obj = Path(asset_path)

            if not asset_path_obj.exists():
                logger.warning(f"Không tìm thấy asset: {asset_path}")
                continue

            logger.info(f"Đang phân tích asset {i}/{total_assets}: {asset_path_obj.name}")

            # Phát tiến độ cho asset này
            progress = 0.01 + (i - 1) / total_assets * 0.14  # 1% - 15%
            self._emit_progress(ProgressEvent(
                event_type="analyzing_asset",
                progress=progress,
                frame_current=i,
                frame_total=total_assets,
                extra_info=asset_path_obj.name
            ))

            # Xác định loại asset
            asset_type = self._get_asset_type(asset_path_obj)

            if asset_type == "image":
                # Phân tích ảnh dùng ImageAnalysisService
                analysis_source = context.request.get("source", "runninghub")
                description = await self.core.image_analysis(asset_path, source=analysis_source)

                self.asset_index[asset_path] = {
                    "path": asset_path,
                    "type": "image",
                    "name": asset_path_obj.name,
                    "description": description
                }

                logger.info(f"✅ Đã phân tích ảnh: {description[:50]}...")

            elif asset_type == "video":
                # Phân tích video dùng VideoAnalysisService
                analysis_source = context.request.get("source", "runninghub")
                try:
                    description = await self.core.video_analysis(asset_path, source=analysis_source)

                    self.asset_index[asset_path] = {
                        "path": asset_path,
                        "type": "video",
                        "name": asset_path_obj.name,
                        "description": description
                    }

                    logger.info(f"✅ Đã phân tích video: {description[:50]}...")
                except Exception as e:
                    logger.warning(f"Phân tích video thất bại cho {asset_path_obj.name}: {e}, đang dùng dự phòng")
                    self.asset_index[asset_path] = {
                        "path": asset_path,
                        "type": "video",
                        "name": asset_path_obj.name,
                        "description": "Asset video (phân tích thất bại)"
                    }

            else:
                logger.warning(f"Loại asset không xác định: {asset_path}")

        logger.success(f"✅ Phân tích asset hoàn thành: đã index {len(self.asset_index)} asset")

        # Lưu asset index vào context
        context.asset_index = self.asset_index
        
        # Emit completion of asset analysis
        self._emit_progress(ProgressEvent(
            event_type="analyzing_assets",
            progress=0.15,
            frame_current=total_assets,
            frame_total=total_assets,
            extra_info="complete"
        ))
        
        return context
    
    async def determine_title(self, context: PipelineContext) -> PipelineContext:
        """
        Dùng tiêu đề người dùng cung cấp nếu có, ngược lại để trống

        Args:
            context: Context pipeline

        Returns:
            Context đã cập nhật với tiêu đề (có thể rỗng)
        """
        title = context.request.get("video_title")

        if title:
            context.title = title
            logger.info(f"📝 Tiêu đề video: {title} (do người dùng chỉ định)")
        else:
            context.title = ""
            logger.info(f"📝 Không có tiêu đề video được chỉ định (sẽ ẩn trong template)")

        return context

    async def generate_content(self, context: PipelineContext) -> PipelineContext:
        """
        Sinh kịch bản video bằng LLM với output có cấu trúc

        LLM trực tiếp gán asset cho các cảnh - không cần logic khớp phức tạp.

        Args:
            context: Context pipeline

        Returns:
            Context đã cập nhật với kịch bản đã sinh (các cảnh đã được gán asset_path)
        """
        from pixelle_video.prompts.asset_script_generation import build_asset_script_prompt

        logger.info("🤖 Đang sinh kịch bản video bằng LLM...")
        
        # Emit progress for script generation (15% - 25%)
        self._emit_progress(ProgressEvent(
            event_type="generating_script",
            progress=0.16
        ))
        
        # Xây dựng prompt cho LLM
        intent = context.request.get("intent", context.input_text)
        duration = context.request.get("duration", 30)
        title = context.title  # Có thể rỗng nếu người dùng không cung cấp

        # Chuẩn bị mô tả asset với đường dẫn đầy đủ để LLM tham chiếu
        asset_info = []
        for asset_path, metadata in self.asset_index.items():
            asset_info.append(f"- Đường dẫn: {asset_path}\n  Mô tả: {metadata['description']}")

        assets_text = "\n".join(asset_info)

        # Xây dựng prompt bằng hàm prompt tập trung
        prompt = build_asset_script_prompt(
            intent=intent,
            duration=duration,
            assets_text=assets_text,
            title=title
        )

        # Gọi LLM với output có cấu trúc
        script: VideoScript = await self.core.llm(
            prompt=prompt,
            response_type=VideoScript,
            temperature=0.8,
            max_tokens=4000
        )

        # Chuyển sang định dạng dict để tương thích với code phía sau
        context.script = [scene.model_dump() for scene in script.scenes]

        # Xác thực asset path có tồn tại
        for scene in context.script:
            asset_path = scene.get("asset_path")
            if asset_path not in self.asset_index:
                # Tìm match gần nhất (trong trường hợp LLM sửa nhẹ đường dẫn)
                matched = False
                for known_path in self.asset_index.keys():
                    if Path(known_path).name == Path(asset_path).name:
                        scene["asset_path"] = known_path
                        matched = True
                        logger.warning(f"Đã sửa đường dẫn asset: {asset_path} -> {known_path}")
                        break

                if not matched:
                    # Dự phòng tới asset đầu tiên có sẵn
                    fallback_path = list(self.asset_index.keys())[0]
                    logger.warning(f"Đường dẫn asset không xác định '{asset_path}', dùng dự phòng: {fallback_path}")
                    scene["asset_path"] = fallback_path

        logger.success(f"✅ Đã sinh kịch bản với {len(context.script)} cảnh")
        
        # Emit progress after script generation
        self._emit_progress(ProgressEvent(
            event_type="generating_script",
            progress=0.25,
            extra_info="complete"
        ))
        
        # Log preview kịch bản
        for scene in context.script:
            narrations = scene.get("narrations", [])
            if isinstance(narrations, str):
                narrations = [narrations]
            narration_preview = " | ".join([n[:30] + "..." if len(n) > 30 else n for n in narrations[:2]])
            asset_name = Path(scene.get("asset_path", "unknown")).name
            logger.info(f"Cảnh {scene['scene_number']} [{asset_name}]: {narration_preview}")

        return context

    async def plan_visuals(self, context: PipelineContext) -> PipelineContext:
        """
        Chuẩn bị các cảnh đã khớp từ kịch bản do LLM sinh

        Vì LLM đã gán asset_path trong generate_content, method này
        chỉ đơn giản chuyển định dạng kịch bản sang định dạng matched_scenes.

        Args:
            context: Context pipeline

        Returns:
            Context đã cập nhật với matched_scenes
        """
        logger.info("🎯 Đang chuẩn bị mapping cảnh-asset...")

        # LLM đã gán asset_path cho mỗi cảnh trong generate_content
        # Chỉ cần chuyển sang định dạng matched_scenes để tương thích với phía sau
        context.matched_scenes = [
            {
                **scene,
                "matched_asset": scene["asset_path"]  # Alias để tương thích
            }
            for scene in context.script
        ]

        # Log tóm tắt sử dụng asset
        asset_usage = {}
        for scene in context.matched_scenes:
            asset = scene["matched_asset"]
            asset_usage[asset] = asset_usage.get(asset, 0) + 1

        logger.info(f"📊 Tóm tắt sử dụng asset:")
        for asset_path, count in asset_usage.items():
            logger.info(f"   {Path(asset_path).name}: {count} cảnh")

        return context

    async def initialize_storyboard(self, context: PipelineContext) -> PipelineContext:
        """
        Khởi tạo storyboard từ các cảnh đã khớp

        Args:
            context: Context pipeline

        Returns:
            Context đã cập nhật với storyboard
        """
        from pixelle_video.models.storyboard import (
            Storyboard,
            StoryboardFrame, 
            StoryboardConfig
        )
        from datetime import datetime
        
        # Trích xuất tất cả thuyết minh theo thứ tự để tương thích
        all_narrations = []
        for scene in context.matched_scenes:
            narrations = scene.get("narrations", [scene.get("narration", "")])
            if isinstance(narrations, str):
                narrations = [narrations]
            all_narrations.extend(narrations)

        context.narrations = all_narrations

        # Lấy kích thước template
        # Dùng template asset_default.html hỗ trợ cả ảnh và video asset
        # (hiển thị background ảnh có điều kiện hoặc cung cấp overlay trong suốt)
        template_name = "1080x1920/asset_default.html"
        # Trích xuất kích thước từ tên template (vd: "1080x1920")
        try:
            dims = template_name.split("/")[0].split("x")
            media_width = int(dims[0])
            media_height = int(dims[1])
        except:
            # Mặc định 1080x1920
            media_width = 1080
            media_height = 1920

        # Tạo StoryboardConfig
        context.config = StoryboardConfig(
            task_id=context.task_id,
            n_storyboard=len(context.matched_scenes),  # Số cảnh
            min_narration_words=5,
            max_narration_words=50,
            video_fps=30,
            tts_inference_mode="local",
            voice_id=context.params.get("voice_id", "zh-CN-YunjianNeural"),
            tts_speed=context.params.get("tts_speed", 1.2),
            media_width=media_width,
            media_height=media_height,
            frame_template=template_name,
            template_params=context.params.get("template_params")
        )
        
        # Tạo Storyboard
        context.storyboard = Storyboard(
            title=context.title,
            config=context.config,
            created_at=datetime.now()
        )

        # Tạo các StoryboardFrame - một frame cho mỗi cảnh
        for i, scene in enumerate(context.matched_scenes):
            # Lấy thuyết minh đầu tiên cho frame (sẽ ghép audio sau)
            narrations = scene.get("narrations", [scene.get("narration", "")])
            if isinstance(narrations, str):
                narrations = [narrations]

            # Dùng thuyết minh đầu tiên làm text chính (cho phụ đề)
            # Sẽ ghép tất cả thuyết minh trong audio
            main_narration = " ".join(narrations)  # Ghép để hiển thị phụ đề

            frame = StoryboardFrame(
                index=i,
                narration=main_narration,
                image_prompt=None,  # Dùng asset của user, không sinh ảnh
                created_at=datetime.now()
            )

            # Lấy asset path và xác định loại media thực từ asset_index
            asset_path = scene["matched_asset"]
            asset_metadata = self.asset_index.get(asset_path, {})
            asset_type = asset_metadata.get("type", "image")  # Mặc định là image nếu không tìm thấy

            # Đặt loại media và path dựa trên loại asset thực
            if asset_type == "video":
                frame.media_type = "video"
                frame.video_path = asset_path
                logger.debug(f"Cảnh {i}: Đang dùng asset video: {Path(asset_path).name}")
            else:
                frame.media_type = "image"
                frame.image_path = asset_path
                logger.debug(f"Cảnh {i}: Đang dùng asset ảnh: {Path(asset_path).name}")

            # Lưu thông tin cảnh để sinh audio sau
            frame._scene_data = scene  # Lưu tạm cho nhiều thuyết minh

            context.storyboard.frames.append(frame)

        logger.info(f"✅ Đã tạo storyboard với {len(context.storyboard.frames)} cảnh")

        return context

    async def produce_assets(self, context: PipelineContext) -> PipelineContext:
        """
        Sinh video cho các cảnh dùng FrameProcessor (asset + nhiều thuyết minh + template)

        Args:
            context: Context pipeline

        Returns:
            Context đã cập nhật với các frame đã xử lý
        """
        logger.info("🎬 Đang sản xuất video cho các cảnh...")
        
        storyboard = context.storyboard
        config = context.config
        total_frames = len(storyboard.frames)
        
        # Progress range: 30% - 85% for frame production
        base_progress = 0.30
        progress_range = 0.55  # 85% - 30%
        
        for i, frame in enumerate(storyboard.frames, 1):
            logger.info(f"Đang sản xuất cảnh {i}/{total_frames}...")

            # Phát tiến độ cho frame này (mỗi frame có 4 bước: audio, combine, duration, compose)
            frame_progress = base_progress + (i - 1) / total_frames * progress_range
            self._emit_progress(ProgressEvent(
                event_type="frame_step",
                progress=frame_progress,
                frame_current=i,
                frame_total=total_frames,
                step=1,
                action="audio"
            ))

            # Lấy dữ liệu cảnh kèm thuyết minh
            scene = frame._scene_data
            narrations = scene.get("narrations", [scene.get("narration", "")])
            if isinstance(narrations, str):
                narrations = [narrations]

            logger.info(f"Cảnh {i} có {len(narrations)} thuyết minh")

            # Bước 1: Sinh audio cho mỗi thuyết minh và ghép
            narration_audios = []
            for j, narration_text in enumerate(narrations, 1):
                audio_path = Path(context.task_dir) / "frames" / f"{i:02d}_narration_{j}.mp3"
                audio_path.parent.mkdir(parents=True, exist_ok=True)

                await self.core.tts(
                    text=narration_text,
                    output_path=str(audio_path),
                    voice_id=config.voice_id,
                    speed=config.tts_speed
                )

                narration_audios.append(str(audio_path))
                logger.debug(f"  Thuyết minh {j}/{len(narrations)}: {narration_text[:30]}...")

            # Ghép tất cả audio thuyết minh cho cảnh này
            if len(narration_audios) > 1:
                from pixelle_video.utils.os_util import get_task_frame_path

                # Phát tiến độ cho việc ghép audio
                frame_progress = base_progress + ((i - 1) + 0.25) / total_frames * progress_range
                self._emit_progress(ProgressEvent(
                    event_type="frame_step",
                    progress=frame_progress,
                    frame_current=i,
                    frame_total=total_frames,
                    step=2,
                    action="audio"
                ))

                combined_audio_path = Path(context.task_dir) / "frames" / f"{i:02d}_audio.mp3"

                # Dùng FFmpeg để ghép các file audio
                import subprocess

                # Tạo danh sách file cho FFmpeg concat
                filelist_path = Path(context.task_dir) / "frames" / f"{i:02d}_audiolist.txt"
                with open(filelist_path, 'w') as f:
                    for audio_file in narration_audios:
                        escaped_path = str(Path(audio_file).absolute()).replace("'", "'\\''")
                        f.write(f"file '{escaped_path}'\n")

                # Ghép các file audio
                concat_cmd = [
                    'ffmpeg',
                    '-f', 'concat',
                    '-safe', '0',
                    '-i', str(filelist_path),
                    '-c', 'copy',
                    '-y',
                    str(combined_audio_path)
                ]

                subprocess.run(concat_cmd, check=True, capture_output=True)
                frame.audio_path = str(combined_audio_path)

                logger.info(f"✅ Đã ghép {len(narration_audios)} thuyết minh thành một audio")
            else:
                frame.audio_path = narration_audios[0]

            # Bước 2: Dùng FrameProcessor để sinh frame đã ghép và video
            # FrameProcessor sẽ xử lý:
            # - Render template (với kích thước phù hợp)
            # - Ghép phụ đề
            # - Tạo segment video
            # - Đặt tên file đúng trong frames/

            # Vì đã có audio và ảnh, ta bỏ qua một số bước
            # bằng cách gọi thủ công các bước ghép

            # Phát tiến độ cho việc tính thời lượng
            frame_progress = base_progress + ((i - 1) + 0.5) / total_frames * progress_range
            self._emit_progress(ProgressEvent(
                event_type="frame_step",
                progress=frame_progress,
                frame_current=i,
                frame_total=total_frames,
                step=3,
                action="compose"
            ))

            # Lấy thời lượng audio làm thời lượng frame
            import subprocess
            duration_cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                frame.audio_path
            ]
            duration_result = subprocess.run(duration_cmd, capture_output=True, text=True, check=True)
            frame.duration = float(duration_result.stdout.strip())

            # Phát tiến độ cho việc ghép video
            frame_progress = base_progress + ((i - 1) + 0.75) / total_frames * progress_range
            self._emit_progress(ProgressEvent(
                event_type="frame_step",
                progress=frame_progress,
                frame_current=i,
                frame_total=total_frames,
                step=4,
                action="video"
            ))

            # Dùng FrameProcessor để ghép đúng cách
            processed_frame = await self.core.frame_processor(
                frame=frame,
                storyboard=storyboard,
                config=config,
                total_frames=total_frames
            )

            logger.success(f"✅ Cảnh {i} hoàn thành")

        # Phát hoàn thành sản xuất frame
        self._emit_progress(ProgressEvent(
            event_type="processing_frame",
            progress=0.85,
            frame_current=total_frames,
            frame_total=total_frames
        ))

        return context

    async def post_production(self, context: PipelineContext) -> PipelineContext:
        """
        Ghép video các cảnh và thêm BGM

        Args:
            context: Context pipeline

        Returns:
            Context đã cập nhật với đường dẫn video cuối cùng
        """
        logger.info("🎞️ Đang ghép các cảnh...")
        
        # Emit progress for concatenation (85% - 95%)
        self._emit_progress(ProgressEvent(
            event_type="concatenating",
            progress=0.86
        ))
        
        # Thu thập các segment video từ frame của storyboard
        scene_videos = [frame.video_segment_path for frame in context.storyboard.frames]

        # Sinh tên file: dùng tiêu đề nếu có, ngược lại dùng task_id hoặc tên mặc định
        if context.title:
            filename = f"{context.title}.mp4"
        else:
            filename = f"{context.task_id}.mp4"  # Dùng task_id làm tên file khi tiêu đề rỗng

        final_video_path = Path(context.task_dir) / filename

        # Lấy tham số BGM
        bgm_path = context.request.get("bgm_path")
        bgm_volume = context.request.get("bgm_volume", 0.2)
        bgm_mode = context.request.get("bgm_mode", "loop")

        if bgm_path:
            logger.info(f"🎵 Đang thêm BGM: {bgm_path} (âm lượng={bgm_volume}, chế độ={bgm_mode})")

        self.core.video.concat_videos(
            videos=scene_videos,
            output=str(final_video_path),
            bgm_path=bgm_path,
            bgm_volume=bgm_volume,
            bgm_mode=bgm_mode
        )

        context.final_video_path = str(final_video_path)
        context.storyboard.final_video_path = str(final_video_path)

        logger.success(f"✅ Video cuối cùng: {final_video_path}")

        # Phát hoàn thành ghép
        self._emit_progress(ProgressEvent(
            event_type="concatenating",
            progress=0.95,
            extra_info="complete"
        ))

        return context

    async def finalize(self, context: PipelineContext) -> PipelineContext:
        """
        Hoàn thiện và trả về kết quả

        Args:
            context: Context pipeline

        Returns:
            Context cuối cùng
        """
        logger.success(f"🎉 Tạo video dựa trên asset hoàn thành!")
        logger.info(f"Video: {context.final_video_path}")
        
        # Emit completion
        self._emit_progress(ProgressEvent(
            event_type="completed",
            progress=1.0
        ))
        
        # Lưu metadata để theo dõi lịch sử
        await self._persist_task_data(context)

        return context

    async def _persist_task_data(self, ctx: PipelineContext):
        """
        Lưu metadata task và storyboard vào filesystem để theo dõi lịch sử
        """
        from pathlib import Path

        try:
            storyboard = ctx.storyboard
            task_id = ctx.task_id

            if not task_id:
                logger.warning("Không có task_id trong context, bỏ qua persistence")
                return
            
            # Get file size
            video_path_obj = Path(ctx.final_video_path)
            file_size = video_path_obj.stat().st_size if video_path_obj.exists() else 0
            
            # Build metadata
            input_params = {
                "text": ctx.input_text,
                "mode": "asset_based",
                "title": ctx.title or "",
                "n_scenes": len(storyboard.frames) if storyboard else 0,
                "assets": ctx.request.get("assets", []),
                "intent": ctx.request.get("intent"),
                "duration": ctx.request.get("duration"),
                "source": ctx.request.get("source"),
                "voice_id": ctx.request.get("voice_id"),
                "tts_speed": ctx.request.get("tts_speed"),
            }
            
            metadata = {
                "task_id": task_id,
                "created_at": storyboard.created_at.isoformat() if storyboard and storyboard.created_at else None,
                "completed_at": storyboard.completed_at.isoformat() if storyboard and storyboard.completed_at else None,
                "status": "completed",
                
                "input": input_params,
                
                "result": {
                    "video_path": ctx.final_video_path,
                    "duration": storyboard.total_duration if storyboard else 0,
                    "file_size": file_size,
                    "n_frames": len(storyboard.frames) if storyboard else 0
                },
                
                "config": {
                    "llm_model": self.core.config.get("llm", {}).get("model", "unknown"),
                    "llm_base_url": self.core.config.get("llm", {}).get("base_url", "unknown"),
                    "source": ctx.request.get("source", "runninghub"),
                }
            }
            
            # Lưu metadata
            await self.core.persistence.save_task_metadata(task_id, metadata)
            logger.info(f"💾 Đã lưu metadata task: {task_id}")

            # Lưu storyboard
            if storyboard:
                await self.core.persistence.save_storyboard(task_id, storyboard)
                logger.info(f"💾 Đã lưu storyboard: {task_id}")

        except Exception as e:
            logger.error(f"Không thể lưu dữ liệu task: {e}")
            # Đừng raise - việc lưu thất bại không nên làm hỏng quá trình tạo video

    # Các method helper

    def _get_asset_type(self, path: Path) -> str:
        """Xác định loại asset từ phần mở rộng file"""
        image_exts = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
        video_exts = {".mp4", ".mov", ".avi", ".mkv", ".webm"}

        ext = path.suffix.lower()

        if ext in image_exts:
            return "image"
        elif ext in video_exts:
            return "video"
        else:
            return "unknown"
    
