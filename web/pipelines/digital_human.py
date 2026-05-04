import os
import time
from pathlib import Path
from typing import Any

import streamlit as st
from loguru import logger
import httpx
from web.i18n import tr, get_language
from web.pipelines.base import PipelineUI, register_pipeline_ui
from web.components.content_input import render_version_info
from web.components.digital_tts_config import render_style_config
from web.utils.async_helpers import run_async
from web.utils.streamlit_helpers import check_and_warn_selfhost_workflow
from pixelle_video.config import config_manager
from pixelle_video.utils.os_util import create_task_output_dir

class DigitalHumanPipelineUI(PipelineUI):
    """
    UI cho Pipeline Sinh Video Digital Human.
    Sinh video từ asset người dùng cung cấp (ảnh, video, audio).
    """
    name = "digital_human"
    icon = "🤖"

    @property
    def display_name(self):
        return tr("pipeline.digital_human.name")

    @property
    def description(self):
        return tr("pipeline.digital_human.description")

    def render(self, pixelle_video: Any):
        # Bố cục ba cột
        left_col, middle_col, right_col = st.columns([1, 1, 1])

        # ====================================================================
        # Cột trái: Tải lên Asset
        # ====================================================================
        with left_col:
            asset_params = self.render_digital_human_input()
            style_params = render_style_config(pixelle_video)
            # bgm_params = render_bgm_section(key_prefix="asset_")
            render_version_info()

        # ====================================================================
        # Cột giữa: Cấu hình video
        # ====================================================================
        with middle_col:
            # Cấu hình style ()
            workflow_path = self.workflow_path_config()
            mode_params = self.render_digital_human_mode(asset_params["character_assets"])

        # ====================================================================
        # Cột phải: Xem trước Output
        # ====================================================================
        with right_col:
            # Gộp tất cả tham số
            video_params = {
                **mode_params,
                **asset_params,
                **style_params,
                "workflow_path": workflow_path
            }

            self._render_output_preview(pixelle_video, video_params)

    def render_digital_human_input(self) -> dict:
        """Render phần tải lên ảnh nhân vật digital human"""
        with st.container(border=True):
            st.markdown(f"**{tr('digital_human.section.character_assets')}**")
            
            with st.expander(tr("help.feature_description"), expanded=False):
                st.markdown(f"**{tr('help.what')}**")
                st.markdown(tr("digital_human.assets.character_what"))
                st.markdown(f"**{tr('help.how')}**")
                st.markdown(tr("digital_human.assets.how"))
            
            # File uploader cho nhiều file
            uploaded_files = st.file_uploader(
                tr("digital_human.assets.upload"),
                type=["jpg", "jpeg", "png", "webp"],
                accept_multiple_files=True,
                help=tr("digital_human.assets.upload_help"),
                key="character_files"
            )

            # Lưu file đã tải lên vào thư mục tạm với session ID duy nhất
            character_asset_paths = []
            if uploaded_files:
                import uuid
                session_id = str(uuid.uuid4()).replace('-', '')[:12]
                temp_dir = Path(f"temp/assets_{session_id}")
                temp_dir.mkdir(parents=True, exist_ok=True)

                for uploaded_file in uploaded_files:
                    file_path = temp_dir / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    character_asset_paths.append(str(file_path.absolute()))

                st.success(tr("digital_human.assets.character_sucess"))

                # Xem trước asset đã tải lên
                with st.expander(tr("digital_human.assets.preview"), expanded=True):
                    # Hiển thị dạng lưới (3 cột)
                    cols = st.columns(3)
                    for i, (file, path) in enumerate(zip(uploaded_files, character_asset_paths)):
                        with cols[i % 3]:
                            # Kiểm tra là ảnh
                            ext = Path(path).suffix.lower()
                            if ext in [".jpg", ".jpeg", ".png", ".webp"]:
                                st.image(file, caption=file.name, use_container_width=True)
            else:
                st.info(tr("digital_human.assets.character_empty_hint"))

            return {"character_assets": character_asset_paths}

    def workflow_path_config(self) -> dict:
        # Chọn nguồn workflow
        with st.container(border=True):
            st.markdown(f"**{tr('asset_based.section.source')}**")
            
            with st.expander(tr("help.feature_description"), expanded=False):
                st.markdown(f"**{tr('help.what')}**")
                st.markdown(tr("asset_based.source.what"))
                st.markdown(f"**{tr('help.how')}**")
                st.markdown(tr("asset_based.source.how"))
            
            source_options = {
                "runninghub": tr("asset_based.source.runninghub"),
                "selfhost": tr("asset_based.source.selfhost")
            }
            
            # Kiểm tra API key RunningHub đã được cấu hình chưa
            comfyui_config = config_manager.get_comfyui_config()
            has_runninghub = bool(comfyui_config.get("runninghub_api_key"))
            has_selfhost = bool(comfyui_config.get("comfyui_url"))

            # Luôn mặc định là runninghub
            default_source_index = 0

            source = st.radio(
                tr("asset_based.source.select"),
                options=list(source_options.keys()),
                format_func=lambda x: source_options[x],
                index=default_source_index,
                horizontal=True,
                key="digital_human_workflow_source",
                label_visibility="collapsed"
            )

            # Khởi tạo workflow_config với giá trị mặc định theo lựa chọn nguồn
            # Đảm bảo biến luôn có giá trị ngay cả khi backend chưa được cấu hình
            if source == "runninghub":
                workflow_config = {
                    "first_workflow_path": "workflows/runninghub/digital_image.json",
                    "second_workflow_path": "workflows/runninghub/digital_combination.json",
                    "third_workflow_path": "workflows/runninghub/digital_customize.json"
                }
                if not has_runninghub:
                    st.warning(tr("asset_based.source.runninghub_not_configured"))
                else:
                    st.info(tr("asset_based.source.runninghub_hint"))
            else:
                workflow_config = {
                    "first_workflow_path": "workflows/selfhost/digital_image.json",
                    "second_workflow_path": "workflows/selfhost/digital_combination.json",
                    "third_workflow_path": "workflows/selfhost/digital_customize.json"
                }
                if not has_selfhost:
                    st.warning(tr("asset_based.source.selfhost_not_configured"))
                else:
                    st.info(tr("asset_based.source.selfhost_hint"))

                    # Kiểm tra và cảnh báo cho các workflow selfhost (tự hiện popup nếu chưa xác nhận)
                    # Cảnh báo cho workflow đầu tiên làm đại diện
                    # TODO: cần kiểm tra workflow có hợp lệ không
                    # check_and_warn_selfhost_workflow("selfhost/digital_image.json")
            return workflow_config

    def render_digital_human_mode(self, character_asset_paths: list) -> dict:
        with st.container(border=True):
            st.markdown(f"**{tr('digital_human.section.select_mode')}**")
            
            with st.expander(tr("help.feature_description"), expanded=False):
                st.markdown(f"**{tr('help.what')}**")
                st.markdown(tr("digital_human.assets.mode_what"))
                st.markdown(f"**{tr('help.how')}**")
                st.markdown(tr("digital_human.assets.select_how"))
            
            mode = st.radio(
                "Chế độ xử lý",
                ["digital", "customize"],
                horizontal=True,
                format_func=lambda x: tr(f"mode.{x}"),
                label_visibility="collapsed",
                key="mode_selection"
                )

            # Ô nhập text (dùng chung cho cả hai chế độ)
            text_placeholder = tr("digital_human.input.topic_placeholder") if mode == "digital" else tr("digital_human.input.content_placeholder")
            text_height = 120 if mode == "digital" else 200
            text_help = tr("input.text_help_digital") if mode == "digital" else tr("input.text_help_fixed")

            if mode == "digital":
                # File uploader cho nhiều file
                uploaded_files = st.file_uploader(
                    tr("digital_human.assets.upload"),
                    type=["jpg", "jpeg", "png", "webp"],
                    accept_multiple_files=True,
                    help=tr("digital_human.assets.upload_help"),
                    key="digital_files"
                )

                # Lưu file đã tải lên vào thư mục tạm với session ID duy nhất
                goods_asset_paths = []
                if uploaded_files:
                    import uuid
                    session_id = str(uuid.uuid4()).replace('-', '')[:12]
                    temp_dir = Path(f"temp/assets_{session_id}")
                    temp_dir.mkdir(parents=True, exist_ok=True)

                    for uploaded_file in uploaded_files:
                        file_path = temp_dir / uploaded_file.name
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        goods_asset_paths.append(str(file_path.absolute()))

                    st.success(tr("digital_human.assets.goods_sucess"))

                    # Xem trước asset đã tải lên
                    with st.expander(tr("digital_human.assets.preview"), expanded=True):
                        # Hiển thị dạng lưới (3 cột)
                        cols = st.columns(3)
                        for i, (file, path) in enumerate(zip(uploaded_files, goods_asset_paths)):
                            with cols[i % 3]:
                                # Kiểm tra là ảnh
                                ext = Path(path).suffix.lower()
                                if ext in [".jpg", ".jpeg", ".png", ".webp"]:
                                    st.image(file, caption=file.name, use_container_width=True)
                else:
                    st.info(tr("digital_human.assets.goods_empty_hint"))
                    # Ô nhập text
                goods_text = st.text_area(
                    tr("digital_human.input_text"),
                    placeholder=text_placeholder,
                    height=text_height,
                    help=text_help,
                    key="digital_box"
                    )

                goods_title = st.text_input(
                    tr("digital_human.goods_title"),
                    placeholder=tr("digital_human.goods_title_placeholder"),
                    help=tr("digital_human.goods_title_help"),
                    key="goods_title"
                )

                return {
                    "character_assets": character_asset_paths,
                    "goods_title": goods_title,
                    "goods_assets": goods_asset_paths,
                    "goods_text": goods_text,
                    "mode": mode
                    }

            else:
                goods_text = st.text_area(
                    tr("digital_human.customize_text"),
                    placeholder=text_placeholder,
                    height=text_height,
                    help=text_help,
                    key="customize_box"
                )

                return {
                    "character_assets": character_asset_paths,
                    "goods_text": goods_text,
                    "mode": mode
                    }
                    
    def _render_output_preview(self, pixelle_video: Any, video_params: dict):
        """Render phần xem trước output"""
        with st.container(border=True):
            st.markdown(f"**{tr('section.video_generation')}**")

            # Kiểm tra cấu hình
            if not config_manager.validate():
                st.warning(tr("settings.not_configured"))

            # Lấy dữ liệu input
            character_assets = video_params.get("character_assets", [])
            goods_assets = video_params.get("goods_assets", [])
            goods_title = video_params.get("goods_title", "")
            goods_text = video_params.get("goods_text", "")
            mode = video_params.get("mode")
            tts_voice = video_params.get("tts_voice", "zh-CN-YunjianNeural")
            tts_speed = video_params.get("tts_speed", 1.2)

            logger.info(f"🔧 Tham số TTS lấy được:")
            logger.info(f"  - tts_voice: {tts_voice}")
            logger.info(f"  - tts_speed: {tts_speed}")
            logger.info(f"  - tts_voice trong video_params: {video_params.get('tts_voice', 'NOT_FOUND')}")
            logger.info(f"  - video_params: {video_params}")

            # Kiểm tra hợp lệ
            if not character_assets:
                st.info(tr("digital_human.assets.character_warning"))
                st.button(
                    tr("btn.generate"),
                    type="primary",
                    use_container_width=True,
                    disabled=True,
                    key="digital_human_generate_disabled"
                )
                return

            if mode == "digital" and not goods_assets:
                st.info(tr("digital_human.assets.goods_warning"))
                st.button(
                    tr("btn.generate"),
                    type="primary",
                    use_container_width=True,
                    disabled=True,
                    key="digital_human_goods_vaiidation"
                )
                return

            if mode == "digital" and not (goods_text or goods_title):
                st.info(tr("digital_human.assets.digital_mode"))
                st.button(
                    tr("btn.generate"),
                    type="primary",
                    use_container_width=True,
                    disabled=True,
                    key="digital_human_digital_disable"
                )
                return
            
            if mode == "digital" and (goods_text or goods_title):
                st.warning(tr("digital_human.assets.digital_mode_warning"))
            
            if mode == "customize" and not goods_text:
                st.info(tr("digital_human.assets.customize_mode"))
                st.button(
                    tr("btn.generate"),
                    type="primary",
                    use_container_width=True,
                    disabled=True,
                    key="digital_human_customize_disable"
                )
                return
            
            # Nút sinh video
            if st.button(tr("btn.generate"), type="primary", use_container_width=True, key="digital_human_generate"):
                # Kiểm tra
                if not config_manager.validate():
                    st.error(tr("settings.not_configured"))
                    st.stop()

                # Hiển thị tiến trình
                progress_bar = st.progress(0)
                status_text = st.empty()

                start_time = time.time()

                try:
                    # Định nghĩa hàm sinh video bất đồng bộ
                    async def generate_digital_human_video():
                        task_dir, task_id = create_task_output_dir()
                        kit = await pixelle_video._get_or_create_comfykit()
                        workflow_path = video_params["workflow_path"]

                        import json
                        from pathlib import Path

                        if mode == "customize":
                            status_text.text(tr("progress.step_audio"))
                            progress_bar.progress(25)
                            generated_image_path = character_assets[0]
                            generated_text = goods_text

                            # TTS
                            audio_path = os.path.join(task_dir, "narration.mp3")
                            tts_inference_mode = video_params.get("tts_inference_mode", "local")
                            tts_voice = video_params.get("tts_voice")
                            tts_speed = video_params.get("tts_speed")
                            tts_workflow = video_params.get("tts_workflow")
                            ref_audio = video_params.get("ref_audio")

                            tts_kwargs = {
                                "text": generated_text,
                                "output_path": audio_path,
                                "inference_mode": tts_inference_mode
                            }
                            if tts_inference_mode == "local":
                                tts_kwargs["voice"] = tts_voice
                                tts_kwargs["speed"] = tts_speed
                            elif tts_inference_mode == "comfyui":
                                if tts_workflow:
                                    tts_kwargs["workflow"] = tts_workflow
                                if ref_audio:
                                    tts_kwargs["ref_audio"] = ref_audio

                            await pixelle_video.tts(**tts_kwargs)
                            progress_bar.progress(65)
                            status_text.text(tr("progress.concatenating"))

                            # Gọi trực tiếp workflow thứ hai
                            second_workflow_path = Path(workflow_path.get("second_workflow_path"))
                            if not second_workflow_path.exists():
                                raise Exception(f"File workflow bước hai không tồn tại:{second_workflow_path}")
                            with open(second_workflow_path, 'r', encoding='utf-8') as f:
                                second_workflow_config = json.load(f)
                            second_workflow_params = {
                                "videoimage": generated_image_path,
                                "audio": audio_path
                            }
                            if second_workflow_config.get("source") == "runninghub" and "workflow_id" in second_workflow_config:
                                workflow_input = second_workflow_config["workflow_id"]
                            else:
                                workflow_input = str(second_workflow_config)
                            second_result = await kit.execute(workflow_input, second_workflow_params)
                            # Trích xuất link video
                            generated_video_url = None
                            if hasattr(second_result, 'videos') and second_result.videos:
                                generated_video_url = second_result.videos[0]
                            elif hasattr(second_result, 'outputs') and second_result.outputs:
                                for node_id, node_output in second_result.outputs.items():
                                    if isinstance(node_output, dict) and 'videos' in node_output:
                                        videos = node_output['videos']
                                        if videos and len(videos) > 0:
                                            generated_video_url = videos[0]
                                            break
                            if not generated_video_url:
                                raise Exception("Workflow bước hai không trả về video. Vui lòng kiểm tra cấu hình workflow.")

                            final_video_path = os.path.join(task_dir, "final.mp4")
                            timeout = httpx.Timeout(300.0)
                            async with httpx.AsyncClient(timeout=timeout) as client:
                                response = await client.get(generated_video_url)
                                response.raise_for_status()
                                with open(final_video_path, 'wb') as f:
                                    f.write(response.content)
                            progress_bar.progress(100)
                            status_text.text(tr("status.success"))
                            return final_video_path

                        else:
                            # Khởi tạo và chuẩn bị tham số
                            task_dir, task_id = create_task_output_dir()
                            logger.info(f"[Khởi tạo] Thư mục task: {task_dir}")

                            first_workflow_path = Path(workflow_path.get("first_workflow_path"))
                            third_workflow_path = Path(workflow_path.get("third_workflow_path"))
                            second_workflow_path = Path(workflow_path.get("second_workflow_path"))
                            assert first_workflow_path.exists(), "File first_workflow không tồn tại."
                            assert third_workflow_path.exists(), "File third_workflow không tồn tại."
                            assert second_workflow_path.exists(), "File second_workflow không tồn tại."

                            if goods_text and goods_text.strip():
                                workflow_path = third_workflow_path
                                workflow_params = {"firstimage": character_assets[0], "secondimage": goods_assets[0]}
                                generated_text = goods_text

                                status_text.text(tr("progress.step_image"))
                                kit = await pixelle_video._get_or_create_comfykit()
                                workflow_config = json.load(open(workflow_path, 'r', encoding='utf8'))
                                if workflow_config.get("source") == "runninghub" and "workflow_id" in workflow_config:
                                    workflow_input = workflow_config["workflow_id"]
                                else:
                                    workflow_input = str(workflow_config)
                                combine_image = await kit.execute(workflow_input, workflow_params)
                                if combine_image.status != "completed":
                                    raise Exception(f"Thực thi workflow thất bại: {combine_image.msg}")
                                generated_image_url = getattr(combine_image, "images", [None])[0]
                                status_text.text(tr("progress.step_audio"))
                                audio_path = os.path.join(task_dir, "narration.mp3")
                                tts_inference_mode = video_params.get("tts_inference_mode", "local")
                                tts_voice = video_params.get("tts_voice")
                                tts_speed = video_params.get("tts_speed")
                                tts_workflow = video_params.get("tts_workflow")
                                ref_audio = video_params.get("ref_audio")

                                tts_kwargs = {
                                    "text": generated_text,
                                    "output_path": audio_path,
                                    "inference_mode": tts_inference_mode
                                }
                                if tts_inference_mode == "local":
                                    tts_kwargs["voice"] = tts_voice
                                    tts_kwargs["speed"] = tts_speed
                                elif tts_inference_mode == "comfyui":
                                    if tts_workflow:
                                        tts_kwargs["workflow"] = tts_workflow
                                    if ref_audio:
                                        tts_kwargs["ref_audio"] = ref_audio

                                await pixelle_video.tts(**tts_kwargs)
                                progress_bar.progress(65)
                                status_text.text(tr("progress.concatenating"))

                                if not second_workflow_path.exists():
                                    raise Exception(f"File workflow bước hai không tồn tại:{second_workflow_path}")
                                with open(second_workflow_path, 'r', encoding='utf-8') as f:
                                    second_workflow_config = json.load(f)
                                second_workflow_params = {
                                    "videoimage": generated_image_url,
                                    "audio": audio_path
                                }
                                if second_workflow_config.get("source") == "runninghub" and "workflow_id" in second_workflow_config:
                                    workflow_input = second_workflow_config["workflow_id"]
                                else:
                                    workflow_input = str(second_workflow_config)
                                second_result = await kit.execute(workflow_input, second_workflow_params)
                                # Trích xuất link video
                                generated_video_url = None
                                if hasattr(second_result, 'videos') and second_result.videos:
                                    generated_video_url = second_result.videos[0]
                                elif hasattr(second_result, 'outputs') and second_result.outputs:
                                    for node_id, node_output in second_result.outputs.items():
                                        if isinstance(node_output, dict) and 'videos' in node_output:
                                            videos = node_output['videos']
                                            if videos and len(videos) > 0:
                                                generated_video_url = videos[0]
                                                break
                                if not generated_video_url:
                                    raise Exception("Workflow bước hai không trả về video. Vui lòng kiểm tra cấu hình workflow.")

                                final_video_path = os.path.join(task_dir, "final.mp4")
                                timeout = httpx.Timeout(300.0)
                                async with httpx.AsyncClient(timeout=timeout) as client:
                                    response = await client.get(generated_video_url)
                                    response.raise_for_status()
                                    with open(final_video_path, 'wb') as f:
                                        f.write(response.content)
                                progress_bar.progress(100)
                                status_text.text(tr("status.success"))
                                return final_video_path

                            else:
                                workflow_path = first_workflow_path
                                workflow_params = {"firstimage": character_assets[0], "secondimage": goods_assets[0], "goodstype": goods_title}

                                status_text.text(tr("progress.step_image"))
                                kit = await pixelle_video._get_or_create_comfykit()
                                workflow_config = json.load(open(workflow_path, 'r', encoding='utf8'))
                                if workflow_config.get("source") == "runninghub" and "workflow_id" in workflow_config:
                                    workflow_input = workflow_config["workflow_id"]
                                else:
                                    workflow_input = str(workflow_config)
                                synthesis_result = await kit.execute(workflow_input, workflow_params)
                                if synthesis_result.status != "completed":
                                    raise Exception(f"Thực thi workflow thất bại: {synthesis_result.msg}")
                                generated_image_url = getattr(synthesis_result, "images", [None])[0]
                                generated_text = getattr(synthesis_result, "texts", [None])[0]
                                
                                status_text.text(tr("progress.step_audio"))
                                audio_path = os.path.join(task_dir, "narration.mp3")
                                tts_inference_mode = video_params.get("tts_inference_mode", "local")
                                tts_voice = video_params.get("tts_voice")
                                tts_speed = video_params.get("tts_speed")
                                tts_workflow = video_params.get("tts_workflow")
                                ref_audio = video_params.get("ref_audio")

                                tts_kwargs = {
                                    "text": generated_text,
                                    "output_path": audio_path,
                                    "inference_mode": tts_inference_mode
                                }
                                if tts_inference_mode == "local":
                                    tts_kwargs["voice"] = tts_voice
                                    tts_kwargs["speed"] = tts_speed
                                elif tts_inference_mode == "comfyui":
                                    if tts_workflow:
                                        tts_kwargs["workflow"] = tts_workflow
                                    if ref_audio:
                                        tts_kwargs["ref_audio"] = ref_audio

                                await pixelle_video.tts(**tts_kwargs)
                                progress_bar.progress(65)
                                status_text.text(tr("progress.concatenating"))

                                if not second_workflow_path.exists():
                                    raise Exception(f"File workflow bước hai không tồn tại:{second_workflow_path}")
                                with open(second_workflow_path, 'r', encoding='utf-8') as f:
                                    second_workflow_config = json.load(f)
                                second_workflow_params = {
                                    "videoimage": generated_image_url,
                                    "audio": audio_path
                                }
                                if second_workflow_config.get("source") == "runninghub" and "workflow_id" in second_workflow_config:
                                    workflow_input = second_workflow_config["workflow_id"]
                                else:
                                    workflow_input = str(second_workflow_config)
                                second_result = await kit.execute(workflow_input, second_workflow_params)
                                # Trích xuất link video
                                generated_video_url = None
                                if hasattr(second_result, 'videos') and second_result.videos:
                                    generated_video_url = second_result.videos[0]
                                elif hasattr(second_result, 'outputs') and second_result.outputs:
                                    for node_id, node_output in second_result.outputs.items():
                                        if isinstance(node_output, dict) and 'videos' in node_output:
                                            videos = node_output['videos']
                                            if videos and len(videos) > 0:
                                                generated_video_url = videos[0]
                                                break
                                if not generated_video_url:
                                    raise Exception("Workflow bước hai không trả về video. Vui lòng kiểm tra cấu hình workflow.")

                                final_video_path = os.path.join(task_dir, "final.mp4")
                                timeout = httpx.Timeout(300.0)
                                async with httpx.AsyncClient(timeout=timeout) as client:
                                    response = await client.get(generated_video_url)
                                    response.raise_for_status()
                                    with open(final_video_path, 'wb') as f:
                                        f.write(response.content)
                                progress_bar.progress(100)
                                status_text.text(tr("status.success"))
                                return final_video_path

                    # Thực thi sinh video bất đồng bộ
                    final_video_path = run_async(generate_digital_human_video())

                    total_time = time.time() - start_time
                    progress_bar.progress(100)
                    status_text.text(tr("status.success"))

                    # Hiển thị kết quả
                    st.success(tr("status.video_generated", path=final_video_path))

                    st.markdown("---")

                    # Thông tin video
                    if os.path.exists(final_video_path):
                        file_size_mb = os.path.getsize(final_video_path) / (1024 * 1024)

                        info_text = (
                            f"⏱️ {tr('info.generation_time')} {total_time:.1f}s   "
                            f"📦 {file_size_mb:.2f}MB"
                        )
                        st.caption(info_text)

                        st.markdown("---")

                        # Xem trước video
                        st.video(final_video_path)

                        # Nút tải xuống
                        with open(final_video_path, "rb") as video_file:
                            video_bytes = video_file.read()
                            video_filename = os.path.basename(final_video_path)
                            st.download_button(
                                label="⬇️ Tải video" if get_language() == "vi_VN" else ("⬇️ 下载视频" if get_language() == "zh_CN" else "⬇️ Download Video"),
                                data=video_bytes,
                                file_name=video_filename,
                                mime="video/mp4",
                                use_container_width=True
                            )
                    else:
                        st.error(tr("status.video_not_found", path=final_video_path))

                except Exception as e:
                    status_text.text("")
                    progress_bar.empty()
                    st.error(tr("status.error", error=str(e)))
                    logger.exception(e)
                    st.stop()


# Tự đăng ký
register_pipeline_ui(DigitalHumanPipelineUI)

