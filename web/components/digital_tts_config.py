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
Component cấu hình style cho web UI (cột giữa)
"""

import os
from pathlib import Path

import streamlit as st
from loguru import logger

from web.i18n import tr, get_language
from web.utils.async_helpers import run_async
from pixelle_video.config import config_manager


def render_style_config(pixelle_video):
    """Render phần cấu hình style (cột giữa)"""
    # Phần TTS (chuyển từ cột trái sang)
    # ====================================================================
    with st.container(border=True):
        st.markdown(f"**{tr('section.tts')}**")

        with st.expander(tr("help.feature_description"), expanded=False):
            st.markdown(f"**{tr('help.what')}**")
            st.markdown(tr("tts.what"))
            st.markdown(f"**{tr('help.how')}**")
            st.markdown(tr("tts.how"))

        # Lấy cấu hình TTS
        comfyui_config = config_manager.get_comfyui_config()
        tts_config = comfyui_config["tts"]

        # Chọn chế độ inference
        tts_mode = st.radio(
            tr("tts.inference_mode"),
            ["local", "comfyui"],
            horizontal=True,
            format_func=lambda x: tr(f"tts.mode.{x}"),
            index=0 if tts_config.get("inference_mode", "local") == "local" else 1,
            key="digital_tts_inference_mode"
        )

        # Hiển thị gợi ý theo chế độ
        if tts_mode == "local":
            st.caption(tr("tts.mode.local_hint"))
        else:
            st.caption(tr("tts.mode.comfyui_hint"))

        # ================================================================
        # UI cho chế độ Local
        # ================================================================
        if tts_mode == "local":
            # Import cấu hình giọng đọc
            from pixelle_video.tts_voices import EDGE_TTS_VOICES, get_voice_display_name

            # Lấy giọng đã lưu trong config
            local_config = tts_config.get("local", {})
            saved_voice = local_config.get("voice", "zh-CN-YunjianNeural")
            saved_speed = local_config.get("speed", 1.2)

            # Xây danh sách lựa chọn giọng kèm i18n
            voice_options = []
            voice_ids = []
            default_voice_index = 0

            for idx, voice_config in enumerate(EDGE_TTS_VOICES):
                voice_id = voice_config["id"]
                display_name = get_voice_display_name(voice_id, tr, get_language())
                voice_options.append(display_name)
                voice_ids.append(voice_id)

                # Đặt index mặc định nếu khớp với giọng đã lưu
                if voice_id == saved_voice:
                    default_voice_index = idx

            # Bố cục hai cột: Giọng | Tốc độ
            voice_col, speed_col = st.columns([1, 1])

            with voice_col:
                # Bộ chọn giọng
                selected_voice_display = st.selectbox(
                    tr("tts.voice_selector"),
                    voice_options,
                    index=default_voice_index,
                    key="digital_tts_local_voice"
                )

                # Lấy ID giọng thực tế
                selected_voice_index = voice_options.index(selected_voice_display)
                selected_voice = voice_ids[selected_voice_index]

            with speed_col:
                # Thanh trượt tốc độ
                tts_speed = st.slider(
                    tr("tts.speed"),
                    min_value=0.5,
                    max_value=2.0,
                    value=saved_speed,
                    step=0.1,
                    format="%.1fx",
                    key="digital_tts_local_speed"
                )
                st.caption(tr("tts.speed_label", speed=f"{tts_speed:.1f}"))

            # Biến cho việc sinh video
            tts_workflow_key = None
            ref_audio_path = None

        # ================================================================
        # UI cho chế độ ComfyUI
        # ================================================================
        else:  # chế độ comfyui
            tts_workflow_key = "runninghub/tts_index2.json"  # giá trị fallback

            # Tải lên audio tham chiếu (tuỳ chọn, dùng để clone giọng)
            ref_audio_file = st.file_uploader(
                tr("tts.ref_audio"),
                type=["mp3", "wav", "flac", "m4a", "aac", "ogg"],
                help=tr("tts.ref_audio_help"),
                key="digital_ref_audio_upload"
            )

            # Lưu ref_audio đã tải lên vào file tạm nếu có
            ref_audio_path = None
            if ref_audio_file is not None:
                # Trình phát nghe thử (phát trực tiếp file vừa upload)
                st.audio(ref_audio_file)

                # Lưu vào thư mục tạm
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                ref_audio_path = temp_dir / f"ref_audio_{ref_audio_file.name}"
                with open(ref_audio_path, "wb") as f:
                    f.write(ref_audio_file.getbuffer())

            # Biến cho việc sinh video
            selected_voice = None
            tts_speed = None

        # ================================================================
        # Nghe thử TTS (dùng được cho cả hai chế độ)
        # ================================================================
        with st.expander(tr("tts.preview_title"), expanded=False):
            # Ô nhập text để nghe thử
            preview_text = st.text_input(
                tr("tts.preview_text"),
                value="Xin chào mọi người, đây là một đoạn giọng nói thử nghiệm.",
                placeholder=tr("tts.preview_text_placeholder"),
                key="digital_tts_preview_text"
            )

            # Nút nghe thử
            if st.button(tr("tts.preview_button"), key="gidital_preview_tts", use_container_width=True):
                with st.spinner(tr("tts.previewing")):
                    try:
                        # Xây tham số TTS theo chế độ
                        tts_params = {
                            "text": preview_text,
                            "inference_mode": tts_mode
                        }

                        if tts_mode == "local":
                            tts_params["voice"] = selected_voice
                            tts_params["speed"] = tts_speed
                        else:  # comfyui
                            tts_params["workflow"] = tts_workflow_key
                            if ref_audio_path:
                                tts_params["ref_audio"] = str(ref_audio_path)

                        audio_path = run_async(pixelle_video.tts(**tts_params))

                        # Phát audio
                        if audio_path:
                            st.success(tr("tts.preview_success"))
                            if os.path.exists(audio_path):
                                st.audio(audio_path, format="audio/mp3")
                            elif audio_path.startswith('http'):
                                st.audio(audio_path)
                            else:
                                st.error("Không thể sinh audio xem trước")

                            # Hiển thị đường dẫn file
                            st.caption(f"📁 {audio_path}")
                        else:
                            st.error("Không thể sinh audio xem trước")
                    except Exception as e:
                        st.error(tr("tts.preview_failed", error=str(e)))
                        logger.exception(e)

    # Trả về toàn bộ tham số cấu hình style (phiên bản đơn giản chỉ TTS local)
    return {
        "tts_inference_mode": tts_mode,
        "tts_voice": selected_voice if tts_mode == "local" else None,
        "tts_speed": tts_speed if tts_mode == "local" else None,
        "tts_workflow": tts_workflow_key if tts_mode == "comfyui" else None,
        "ref_audio": str(ref_audio_path) if ref_audio_path else None,
    }