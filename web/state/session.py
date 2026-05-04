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
Quản lý session state cho web UI
"""

import streamlit as st
from loguru import logger

from web.i18n import get_language, set_language
from web.utils.async_helpers import run_async


def init_session_state():
    """Khởi tạo các biến session state"""
    if "language" not in st.session_state:
        # Dùng ngôn ngữ hệ thống tự phát hiện
        st.session_state.language = get_language()


def init_i18n():
    """Khởi tạo đa ngôn ngữ (i18n)"""
    # Các locale đã được load và ngôn ngữ hệ thống đã được phát hiện khi import
    # Lấy ngôn ngữ từ session state hoặc dùng ngôn ngữ hệ thống đã phát hiện
    if "language" not in st.session_state:
        st.session_state.language = get_language()  # Dùng ngôn ngữ tự phát hiện

    # Đặt ngôn ngữ hiện tại
    set_language(st.session_state.language)


def get_pixelle_video():
    """
    Lấy instance Pixelle-Video đã khởi tạo với cache và cleanup phù hợp

    Dùng st.session_state để cache instance theo session người dùng.
    ComfyKit được khởi tạo lười và tự động tạo lại khi config thay đổi.
    """
    from pixelle_video.service import PixelleVideoCore
    from pixelle_video.config import config_manager

    # Tính hash config để phát hiện thay đổi
    import hashlib
    import json
    config_dict = config_manager.config.to_dict()
    # Chỉ theo dõi config ComfyUI cho hash (các thay đổi config khác không cần tạo lại core)
    comfyui_config = config_dict.get("comfyui", {})
    config_hash = hashlib.md5(json.dumps(comfyui_config, sort_keys=True).encode()).hexdigest()

    # Kiểm tra có cần tạo hoặc tạo lại instance core không
    need_recreate = False
    if 'pixelle_video' not in st.session_state:
        need_recreate = True
        logger.info("Tạo instance PixelleVideoCore mới (lần đầu tiên)")
    elif st.session_state.get('pixelle_video_config_hash') != config_hash:
        need_recreate = True
        logger.info("Cấu hình đã thay đổi, đang tạo lại instance PixelleVideoCore")
        # Dọn dẹp instance cũ
        old_core = st.session_state.pixelle_video
        try:
            run_async(old_core.cleanup())
        except Exception as e:
            logger.warning(f"Không thể dọn dẹp PixelleVideoCore cũ: {e}")

    if need_recreate:
        # Tạo và khởi tạo instance mới
        pixelle_video = PixelleVideoCore()
        run_async(pixelle_video.initialize())

        # Cache trong session state
        st.session_state.pixelle_video = pixelle_video
        st.session_state.pixelle_video_config_hash = config_hash
        logger.info("✅ Đã khởi tạo và cache PixelleVideoCore")
    else:
        pixelle_video = st.session_state.pixelle_video
        logger.debug("Tái sử dụng instance PixelleVideoCore đã cache")

    return pixelle_video

