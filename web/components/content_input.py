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
Component nhập nội dung cho web UI (cột trái)
"""

import streamlit as st

from web.i18n import tr
from web.utils.async_helpers import get_project_version


def render_content_input():
    """Render phần nhập nội dung (cột trái) có hỗ trợ batch"""
    with st.container(border=True):
        st.markdown(f"**{tr('section.content_input')}**")

        # ====================================================================
        # Bước 1: Bật/tắt chế độ batch (ưu tiên cao nhất)
        # ====================================================================
        batch_mode = st.checkbox(
            tr("batch.mode_label"),
            value=False,
            help=tr("batch.mode_help")
        )

        if not batch_mode:
            # ================================================================
            # Chế độ tác vụ đơn (logic gốc, không đổi)
            # ================================================================
            # Chọn chế độ xử lý
            mode = st.radio(
                "Chế độ xử lý",
                ["generate", "fixed"],
                horizontal=True,
                format_func=lambda x: tr(f"mode.{x}"),
                label_visibility="collapsed"
            )

            # Ô nhập text (dùng chung cho cả hai chế độ)
            text_placeholder = tr("input.topic_placeholder") if mode == "generate" else tr("input.content_placeholder")
            text_height = 120 if mode == "generate" else 200
            text_help = tr("input.text_help_generate") if mode == "generate" else tr("input.text_help_fixed")

            text = st.text_area(
                tr("input.text"),
                placeholder=text_placeholder,
                height=text_height,
                help=text_help
            )

            # Bộ chọn chế độ chia (chỉ hiển thị ở chế độ fixed)
            if mode == "fixed":
                split_mode_options = {
                    "paragraph": tr("split.mode_paragraph"),
                    "line": tr("split.mode_line"),
                    "sentence": tr("split.mode_sentence"),
                }
                split_mode = st.selectbox(
                    tr("split.mode_label"),
                    options=list(split_mode_options.keys()),
                    format_func=lambda x: split_mode_options[x],
                    index=0,  # Mặc định chia theo đoạn
                    help=tr("split.mode_help")
                )
            else:
                split_mode = "paragraph"  # Mặc định cho chế độ generate (không sử dụng)

            # Ô nhập tiêu đề (tuỳ chọn cho cả hai chế độ)
            title = st.text_input(
                tr("input.title"),
                placeholder=tr("input.title_placeholder"),
                help=tr("input.title_help")
            )

            # Số phân cảnh (chỉ hiển thị ở chế độ generate)
            if mode == "generate":
                n_scenes = st.slider(
                    tr("video.frames"),
                    min_value=3,
                    max_value=30,
                    value=5,
                    help=tr("video.frames_help"),
                    label_visibility="collapsed"
                )
                st.caption(tr("video.frames_label", n=n_scenes))
            else:
                # Chế độ fixed: bỏ qua n_scenes, đặt giá trị mặc định
                n_scenes = 5
                st.info(tr("video.frames_fixed_mode_hint"))

            return {
                "batch_mode": False,
                "mode": mode,
                "text": text,
                "title": title,
                "n_scenes": n_scenes,
                "split_mode": split_mode
            }

        else:
            # ================================================================
            # Chế độ batch (phiên bản đơn giản hoá YAGNI)
            # ================================================================
            st.markdown(f"**{tr('batch.section_title')}**")
            
            # Thông tin quy tắc batch
            st.info(f"""
**{tr('batch.rules_title')}**
- ✅ {tr('batch.rule_1')}
- ✅ {tr('batch.rule_2')}
- ✅ {tr('batch.rule_3')}
            """)

            # Ô nhập danh sách chủ đề batch
            text_input = st.text_area(
                tr("batch.topics_label"),
                height=300,
                placeholder=tr("batch.topics_placeholder"),
                help=tr("batch.topics_help")
            )

            # Tách chủ đề theo dòng
            if text_input:
                # Tách đơn giản theo dòng, lọc các dòng trống
                topics = [
                    line.strip()
                    for line in text_input.strip().split('\n')
                    if line.strip()
                ]

                if topics:
                    # Kiểm tra giới hạn số lượng
                    if len(topics) > 100:
                        st.error(tr("batch.count_error", count=len(topics)))
                        topics = []
                    else:
                        st.success(tr("batch.count_success", count=len(topics)))

                        # Xem trước danh sách chủ đề
                        with st.expander(tr("batch.preview_title"), expanded=False):
                            for i, topic in enumerate(topics, 1):
                                st.markdown(f"`{i}.` {topic}")
                else:
                    topics = []
            else:
                topics = []

            st.markdown("---")

            # Tiền tố tiêu đề (tuỳ chọn)
            title_prefix = st.text_input(
                tr("batch.title_prefix_label"),
                placeholder=tr("batch.title_prefix_placeholder"),
                help=tr("batch.title_prefix_help")
            )

            # Số phân cảnh (dùng chung cho mọi video)
            n_scenes = st.slider(
                tr("batch.n_scenes_label"),
                min_value=3,
                max_value=30,
                value=5,
                help=tr("batch.n_scenes_help")
            )
            st.caption(tr("batch.n_scenes_caption", n=n_scenes))

            # Thông tin cấu hình
            st.info(f"📌 {tr('batch.config_info')}")

            return {
                "batch_mode": True,
                "topics": topics,
                "mode": "generate",  # Cố định để AI sinh nội dung
                "title_prefix": title_prefix,
                "n_scenes": n_scenes,
            }


def render_bgm_section(key_prefix=""):
    """Render phần chọn BGM"""
    with st.container(border=True):
        st.markdown(f"**{tr('section.bgm')}**")

        with st.expander(tr("help.feature_description"), expanded=False):
            st.markdown(f"**{tr('help.what')}**")
            st.markdown(tr("bgm.what"))
            st.markdown(f"**{tr('help.how')}**")
            st.markdown(tr("bgm.how"))

        # Quét động thư mục bgm để lấy file nhạc (gộp từ bgm/ và data/bgm/)
        from pixelle_video.utils.os_util import list_resource_files

        try:
            all_files = list_resource_files("bgm")
            # Chỉ lọc các file âm thanh
            audio_extensions = ('.mp3', '.wav', '.flac', '.m4a', '.aac', '.ogg')
            bgm_files = sorted([f for f in all_files if f.lower().endswith(audio_extensions)])
        except Exception as e:
            st.warning(f"Không tải được danh sách BGM: {e}")
            bgm_files = []

        # Thêm tuỳ chọn đặc biệt "None"
        bgm_options = [tr("bgm.none")] + bgm_files

        # Mặc định "default.mp3" nếu có, nếu không lấy lựa chọn đầu tiên
        default_index = 0
        if "default.mp3" in bgm_files:
            default_index = bgm_options.index("default.mp3")

        bgm_choice = st.selectbox(
            "BGM",
            bgm_options,
            index=default_index,
            label_visibility="collapsed",
            key=f"{key_prefix}bgm_selector"
        )

        # Thanh trượt âm lượng BGM (chỉ hiển thị khi đã chọn BGM)
        if bgm_choice != tr("bgm.none"):
            bgm_volume = st.slider(
                tr("bgm.volume"),
                min_value=0.0,
                max_value=0.5,
                value=0.2,
                step=0.01,
                format="%.2f",
                key=f"{key_prefix}bgm_volume_slider",
                help=tr("bgm.volume_help")
            )
        else:
            bgm_volume = 0.2  # Giá trị mặc định khi không chọn BGM

        # Nút nghe thử BGM (chỉ khi BGM khác "None")
        if bgm_choice != tr("bgm.none"):
            if st.button(tr("bgm.preview"), key=f"{key_prefix}preview_bgm", use_container_width=True):
                from pixelle_video.utils.os_util import get_resource_path, resource_exists
                try:
                    if resource_exists("bgm", bgm_choice):
                        bgm_file_path = get_resource_path("bgm", bgm_choice)
                        st.audio(bgm_file_path)
                    else:
                        st.error(tr("bgm.preview_failed", file=bgm_choice))
                except Exception as e:
                    st.error(f"{tr('bgm.preview_failed', file=bgm_choice)}: {e}")

        # Dùng tên file đầy đủ cho bgm_path (kèm phần mở rộng)
        bgm_path = None if bgm_choice == tr("bgm.none") else bgm_choice

    return {
        "bgm_path": bgm_path,
        "bgm_volume": bgm_volume
    }


def render_version_info():
    """Render thông tin phiên bản và liên kết GitHub"""
    with st.container(border=True):
        st.markdown(f"**{tr('version.title')}**")
        version = get_project_version()
        github_url = "https://github.com/AIDC-AI/Pixelle-Video"

        # Phiên bản và liên kết GitHub trên cùng một dòng
        github_url = "https://github.com/AIDC-AI/Pixelle-Video"
        badge_url = "https://img.shields.io/github/stars/AIDC-AI/Pixelle-Video"

        st.markdown(
            f'{tr("version.current")}: `{version}` &nbsp;&nbsp; '
            f'<a href="{github_url}" target="_blank">'
            f'<img src="{badge_url}" alt="GitHub stars" style="vertical-align: middle;">'
            f'</a>',
            unsafe_allow_html=True)

