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
Trang chủ - Giao diện sinh video chính
"""

import sys
from pathlib import Path

# Thêm thư mục gốc dự án vào sys.path
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st

# Import quản lý state
from web.state.session import init_session_state, init_i18n, get_pixelle_video

# Import các component
from web.components.header import render_header
from web.components.settings import render_advanced_settings
from web.components.faq import render_faq_sidebar

# Cấu hình trang
st.set_page_config(
    page_title="Trang chủ - Pixelle-Video",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def main():
    """Điểm khởi chạy UI chính"""
    # Khởi tạo session state và i18n
    init_session_state()
    init_i18n()

    # Render header (tiêu đề + bộ chọn ngôn ngữ)
    render_header()

    # Render FAQ trong sidebar
    render_faq_sidebar()

    # Khởi tạo Pixelle-Video
    pixelle_video = get_pixelle_video()

    # Render cấu hình hệ thống (LLM + ComfyUI)
    render_advanced_settings()

    # ========================================================================
    # Chọn và uỷ quyền Pipeline
    # ========================================================================
    from web.pipelines import get_all_pipeline_uis

    # Lấy tất cả pipeline đã đăng ký
    pipelines = get_all_pipeline_uis()

    # Sử dụng Tabs để chọn pipeline
    # Lưu ý: st.tabs trả về danh sách container, mỗi tab một container
    tab_labels = [f"{p.icon} {p.display_name}" for p in pipelines]
    tabs = st.tabs(tab_labels)

    # Render mỗi pipeline trong tab tương ứng
    for i, pipeline in enumerate(pipelines):
        with tabs[i]:
            # Hiển thị mô tả nếu có
            if pipeline.description:
                st.caption(pipeline.description)

            # Uỷ quyền render
            pipeline.render(pixelle_video)


if __name__ == "__main__":
    main()

