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
UI cho Pipeline Standard

Cài đặt bố cục 3 cột kinh điển cho Pipeline Standard.
"""

import streamlit as st
from typing import Any
from web.i18n import tr

from web.pipelines.base import PipelineUI, register_pipeline_ui

# Import các component
from web.components.content_input import render_content_input, render_bgm_section, render_version_info
from web.components.style_config import render_style_config
from web.components.output_preview import render_output_preview


class StandardPipelineUI(PipelineUI):
    """
    UI cho Pipeline Sinh Video Tiêu Chuẩn.
    Cài đặt bố cục 3 cột kinh điển.
    """
    name = "quick_create"
    icon = "⚡"

    @property
    def display_name(self):
        return tr("pipeline.quick_create.name")

    @property
    def description(self):
        return tr("pipeline.quick_create.description")

    def render(self, pixelle_video: Any):
        # Bố cục ba cột
        left_col, middle_col, right_col = st.columns([1, 1, 1])

        # ====================================================================
        # Cột trái: Nhập nội dung & BGM
        # ====================================================================
        with left_col:
            # Nhập nội dung (mode, text, title, n_scenes)
            content_params = render_content_input()

            # Chọn BGM (bgm_path, bgm_volume)
            bgm_params = render_bgm_section()

            # Thông tin phiên bản & liên kết GitHub
            render_version_info()

        # ====================================================================
        # Cột giữa: Cấu hình Style
        # ====================================================================
        with middle_col:
            # Cấu hình style (TTS, template, workflow, v.v.)
            style_params = render_style_config(pixelle_video)

        # ====================================================================
        # Cột phải: Xem trước Output
        # ====================================================================
        with right_col:
            # Gộp tất cả tham số
            video_params = {
                "pipeline": self.name,
                **content_params,
                **bgm_params,
                **style_params
            }

            # Render xem trước output (nút sinh, tiến trình, xem trước video)
            render_output_preview(pixelle_video, video_params)


# Tự đăng ký
register_pipeline_ui(StandardPipelineUI)
