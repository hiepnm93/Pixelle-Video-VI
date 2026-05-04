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
Component xem trước output cho web UI (cột phải)
"""

import base64
import os
from pathlib import Path

import streamlit as st
from loguru import logger

from web.i18n import tr, get_language
from web.utils.async_helpers import run_async
from pixelle_video.models.progress import ProgressEvent
from pixelle_video.config import config_manager


def render_output_preview(pixelle_video, video_params):
    """Render phần xem trước output (cột phải)"""
    # Kiểm tra có ở chế độ batch không
    is_batch = video_params.get("batch_mode", False)

    if is_batch:
        # Chế độ sinh hàng loạt
        render_batch_output(pixelle_video, video_params)
    else:
        # Chế độ sinh một video (logic gốc)
        render_single_output(pixelle_video, video_params)


def render_single_output(pixelle_video, video_params):
    """Render output sinh một video (logic gốc, không đổi)"""
    # Trích xuất các tham số từ dict video_params
    text = video_params.get("text", "")
    mode = video_params.get("mode", "generate")
    title = video_params.get("title")
    n_scenes = video_params.get("n_scenes", 5)
    split_mode = video_params.get("split_mode", "paragraph")
    bgm_path = video_params.get("bgm_path")
    bgm_volume = video_params.get("bgm_volume", 0.2)
    
    tts_mode = video_params.get("tts_inference_mode", "local")
    selected_voice = video_params.get("tts_voice")
    tts_speed = video_params.get("tts_speed")
    tts_workflow_key = video_params.get("tts_workflow")
    ref_audio_path = video_params.get("ref_audio")
    
    frame_template = video_params.get("frame_template")
    custom_values_for_video = video_params.get("template_params", {})
    workflow_key = video_params.get("media_workflow")
    prompt_prefix = video_params.get("prompt_prefix", "")
    
    with st.container(border=True):
        st.markdown(f"**{tr('section.video_generation')}**")

        # Kiểm tra hệ thống đã cấu hình chưa
        if not config_manager.validate():
            st.warning(tr("settings.not_configured"))

        # Nút Tạo
        if st.button(tr("btn.generate"), type="primary", use_container_width=True):
            # Kiểm tra cấu hình hệ thống
            if not config_manager.validate():
                st.error(tr("settings.not_configured"))
                st.stop()

            # Kiểm tra dữ liệu nhập
            if not text:
                st.error(tr("error.input_required"))
                st.stop()

            # Hiển thị tiến trình
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Ghi nhận thời gian bắt đầu cho việc sinh video
            import time
            start_time = time.time()

            try:
                # Callback tiến trình để cập nhật UI
                def update_progress(event: ProgressEvent):
                    """Cập nhật thanh tiến trình và text trạng thái từ ProgressEvent"""
                    # Dịch event thành thông điệp hiển thị cho người dùng
                    if event.event_type == "frame_step":
                        # Frame step: "Phân cảnh 3/5 - Bước 2/4: Sinh hình minh hoạ"
                        action_key = f"progress.step_{event.action}"
                        action_text = tr(action_key)
                        message = tr(
                            "progress.frame_step",
                            current=event.frame_current,
                            total=event.frame_total,
                            step=event.step,
                            action=action_text
                        )
                    elif event.event_type == "processing_frame":
                        # Processing frame: "Phân cảnh 3/5"
                        message = tr(
                            "progress.frame",
                            current=event.frame_current,
                            total=event.frame_total
                        )
                    else:
                        # Sự kiện đơn giản: dùng key i18n trực tiếp
                        message = tr(f"progress.{event.event_type}")

                    # Nối thêm extra_info nếu có (ví dụ: tiến trình batch)
                    if event.extra_info:
                        message = f"{message} - {event.extra_info}"

                    status_text.text(message)
                    progress_bar.progress(min(int(event.progress * 100), 99))  # Giới hạn ở 99% cho đến khi hoàn tất

                # Sinh video (truyền trực tiếp các tham số)
                # Lưu ý: media_width và media_height được xác định tự động từ template
                video_params = {
                    "text": text,
                    "mode": mode,
                    "title": title if title else None,
                    "n_scenes": n_scenes,
                    "split_mode": split_mode,
                    "media_workflow": workflow_key,
                    "frame_template": frame_template,
                    "prompt_prefix": prompt_prefix,
                    "bgm_path": bgm_path,
                    "bgm_volume": bgm_volume if bgm_path else 0.2,
                    "progress_callback": update_progress,
                    "media_width": st.session_state.get('template_media_width'),
                    "media_height": st.session_state.get('template_media_height'),
                }
                
                # Thêm tham số TTS theo chế độ
                video_params["tts_inference_mode"] = tts_mode
                if tts_mode == "local":
                    video_params["tts_voice"] = selected_voice
                    video_params["tts_speed"] = tts_speed
                else:  # comfyui
                    video_params["tts_workflow"] = tts_workflow_key
                    if ref_audio_path:
                        video_params["ref_audio"] = str(ref_audio_path)

                # Thêm tham số template tuỳ chỉnh nếu có
                if custom_values_for_video:
                    video_params["template_params"] = custom_values_for_video

                result = run_async(pixelle_video.generate_video(**video_params))

                # Tính tổng thời gian sinh video
                total_generation_time = time.time() - start_time

                progress_bar.progress(100)
                status_text.text(tr("status.success"))

                # Hiển thị thông báo thành công
                st.success(tr("status.video_generated", path=result.video_path))

                st.markdown("---")

                # Thông tin video (hiển thị gọn)
                file_size_mb = result.file_size / (1024 * 1024)

                # Phân tích kích thước video từ đường dẫn template
                from pixelle_video.utils.template_util import parse_template_size, resolve_template_path
                template_path = resolve_template_path(result.storyboard.config.frame_template)
                video_width, video_height = parse_template_size(template_path)
                
                info_text = (
                    f"⏱️ {tr('info.generation_time')} {total_generation_time:.1f}s   "
                    f"📦 {file_size_mb:.2f}MB   "
                    f"🎬 {len(result.storyboard.frames)}{tr('info.scenes_unit')}   "
                    f"📐 {video_width}x{video_height}"
                )
                st.caption(info_text)
                
                st.markdown("---")

                # Xem trước video
                if os.path.exists(result.video_path):
                    st.video(result.video_path)

                    # Nút tải xuống
                    with open(result.video_path, "rb") as video_file:
                        video_bytes = video_file.read()
                        video_filename = os.path.basename(result.video_path)
                        st.download_button(
                            label="⬇️ Tải video" if get_language() == "vi_VN" else ("⬇️ 下载视频" if get_language() == "zh_CN" else "⬇️ Download Video"),
                            data=video_bytes,
                            file_name=video_filename,
                            mime="video/mp4",
                            use_container_width=True
                        )
                else:
                    st.error(tr("status.video_not_found", path=result.video_path))

            except Exception as e:
                status_text.text("")
                progress_bar.empty()
                st.error(tr("status.error", error=str(e)))
                logger.exception(e)
                st.stop()


def render_batch_output(pixelle_video, video_params):
    """Render output sinh hàng loạt (tối giản, chuyển hướng sang Lịch sử)"""
    topics = video_params.get("topics", [])

    with st.container(border=True):
        st.markdown(f"**{tr('batch.section_generation')}**")

        # Kiểm tra đã có chủ đề chưa
        if not topics:
            st.warning(tr("batch.no_topics"))
            return

        # Kiểm tra cấu hình hệ thống
        if not config_manager.validate():
            st.warning(tr("settings.not_configured"))
            return

        batch_count = len(topics)

        # Hiển thị thông tin batch
        st.info(tr("batch.prepare_info", count=batch_count))

        # Thời gian ước tính (tuỳ chọn)
        estimated_minutes = batch_count * 3  # Ước tính 3 phút mỗi video
        st.caption(tr("batch.estimated_time", minutes=estimated_minutes))
        
        # Nút sinh video với ngữ nghĩa batch
        if st.button(
            tr("batch.generate_button", count=batch_count),
            type="primary",
            use_container_width=True,
            help=tr("batch.generate_help")
        ):
            # Chuẩn bị cấu hình dùng chung
            shared_config = {
                "title_prefix": video_params.get("title_prefix"),
                "n_scenes": video_params.get("n_scenes") or 5,
                "media_workflow": video_params.get("media_workflow"),
                "frame_template": video_params.get("frame_template"),
                "prompt_prefix": video_params.get("prompt_prefix") or "",
                "bgm_path": video_params.get("bgm_path"),
                "bgm_volume": video_params.get("bgm_volume") or 0.2,
                "tts_inference_mode": video_params.get("tts_inference_mode") or "local",
                "media_width": video_params.get("media_width"),
                "media_height": video_params.get("media_height"),
            }
            
            # Thêm tham số TTS theo chế độ (chỉ thêm các giá trị khác None)
            if shared_config["tts_inference_mode"] == "local":
                tts_voice = video_params.get("tts_voice")
                tts_speed = video_params.get("tts_speed")
                if tts_voice:
                    shared_config["tts_voice"] = tts_voice
                if tts_speed:
                    shared_config["tts_speed"] = tts_speed
            else:  # comfyui
                tts_workflow = video_params.get("tts_workflow")
                if tts_workflow:
                    shared_config["tts_workflow"] = tts_workflow
                ref_audio = video_params.get("ref_audio")
                if ref_audio:
                    shared_config["ref_audio"] = str(ref_audio)

            # Thêm tham số template
            if video_params.get("template_params"):
                shared_config["template_params"] = video_params["template_params"]

            # Container UI
            overall_progress_container = st.container()
            current_task_container = st.container()

            # UI tiến trình tổng thể
            overall_progress_bar = overall_progress_container.progress(0)
            overall_status = overall_progress_container.empty()

            # UI tiến trình tác vụ hiện tại
            current_task_title = current_task_container.empty()
            current_task_progress = current_task_container.progress(0)
            current_task_status = current_task_container.empty()

            # Callback tiến trình tổng thể
            def update_overall_progress(current, total, topic):
                progress = (current - 1) / total
                overall_progress_bar.progress(progress)
                overall_status.markdown(
                    f"📊 **{tr('batch.overall_progress')}**: {current}/{total} ({int(progress * 100)}%)"
                )

            # Factory tạo callback tiến trình cho từng tác vụ
            def make_task_progress_callback(task_idx, topic):
                def callback(event: ProgressEvent):
                    # Hiển thị tiêu đề tác vụ hiện tại
                    current_task_title.markdown(f"🎬 **{tr('batch.current_task')} {task_idx}**: {topic}")

                    # Cập nhật tiến trình chi tiết của tác vụ
                    if event.event_type == "frame_step":
                        action_key = f"progress.step_{event.action}"
                        action_text = tr(action_key)
                        message = tr(
                            "progress.frame_step",
                            current=event.frame_current,
                            total=event.frame_total,
                            step=event.step,
                            action=action_text
                        )
                    elif event.event_type == "processing_frame":
                        message = tr(
                            "progress.frame",
                            current=event.frame_current,
                            total=event.frame_total
                        )
                    else:
                        message = tr(f"progress.{event.event_type}")
                    
                    current_task_progress.progress(event.progress)
                    current_task_status.text(message)
                
                return callback

            # Thực thi sinh hàng loạt
            from web.utils.batch_manager import SimpleBatchManager
            import time

            batch_manager = SimpleBatchManager()
            start_time = time.time()

            batch_result = batch_manager.execute_batch(
                pixelle_video=pixelle_video,
                topics=topics,
                shared_config=shared_config,
                overall_progress_callback=update_overall_progress,
                task_progress_callback_factory=make_task_progress_callback
            )

            total_time = time.time() - start_time

            # Xoá hiển thị tiến trình
            overall_progress_bar.progress(1.0)
            overall_status.markdown(f"✅ **{tr('batch.completed')}**")
            current_task_title.empty()
            current_task_progress.empty()
            current_task_status.empty()

            # Hiển thị tổng kết kết quả
            st.markdown("---")
            st.markdown(f"**{tr('batch.results_title')}**")

            col1, col2, col3 = st.columns(3)
            col1.metric(tr("batch.total"), batch_result["total_count"])
            col2.metric(f"✅ {tr('batch.success')}", batch_result["success_count"])
            col3.metric(f"❌ {tr('batch.failed')}", batch_result["failed_count"])

            # Hiển thị tổng thời gian
            minutes = int(total_time / 60)
            seconds = int(total_time % 60)
            st.caption(f"⏱️ {tr('batch.total_time')}: {minutes}{tr('batch.minutes')}{seconds}{tr('batch.seconds')}")

            # Chuyển hướng sang trang Lịch sử
            st.markdown("---")
            st.success(tr("batch.success_message"))
            st.info(tr("batch.view_in_history"))

            # Nút chuyển sang trang Lịch sử bằng cách điều hướng URL JavaScript
            st.markdown(
                f"""
                <a href="/History" target="_blank">
                    <button style="
                        width: 100%;
                        padding: 0.5rem 1rem;
                        background-color: white;
                        color: rgb(49, 51, 63);
                        border: 1px solid rgba(49, 51, 63, 0.2);
                        border-radius: 0.5rem;
                        cursor: pointer;
                        font-size: 1rem;
                        font-weight: 400;
                        text-align: center;
                    ">
                        📚 {tr('batch.goto_history')}
                    </button>
                </a>
                """,
                unsafe_allow_html=True
            )
            
            # Hiển thị các tác vụ thất bại nếu có
            if batch_result["errors"]:
                st.markdown("---")
                st.markdown(f"#### {tr('batch.failed_list')}")

                for item in batch_result["errors"]:
                    with st.expander(f"🔴 {tr('batch.task')} {item['index']}: {item['topic']}", expanded=False):
                        st.error(f"**{tr('batch.error')}**: {item['error']}")

                        # Lỗi chi tiết (đã thu gọn)
                        with st.expander(tr("batch.error_detail")):
                            st.code(item['traceback'], language="python")
    
