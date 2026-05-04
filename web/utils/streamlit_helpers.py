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
Các hàm trợ giúp cho Streamlit
"""

import streamlit as st
import streamlit.components.v1 as components

from web.i18n import tr
from pixelle_video.config import config_manager


def safe_rerun():
    """Rerun an toàn, hoạt động với cả phiên bản Streamlit cũ và mới"""
    if hasattr(st, 'rerun'):
        st.rerun()
    else:
        st.experimental_rerun()


# ============================================================================
# Cảnh báo workflow SelfHost - Dùng alert JavaScript gốc
# ============================================================================
# Dùng alert() gốc của trình duyệt để tránh hạn chế dialog của Streamlit.
# Đơn giản, tin cậy, hoạt động trên mọi trình duyệt.

def check_and_warn_selfhost_workflow(workflow_path: str):
    """
    Kiểm tra xem người dùng vừa chuyển sang workflow selfhost và hiển thị alert JS.

    Sử dụng alert() JavaScript gốc, vượt qua mọi hạn chế dialog của Streamlit.
    Alert hiện ngay khi người dùng chuyển sang workflow selfhost.

    Args:
        workflow_path: Đường dẫn workflow (ví dụ: "selfhost/image_flux.json")
    """
    if not workflow_path:
        return

    # Kiểm tra có phải chuyển SANG selfhost không
    is_selfhost = workflow_path.startswith("selfhost/")

    # Chỉ hiển thị alert khi chuyển SANG selfhost
    if is_selfhost:
        _show_js_alert(workflow_path)


def _show_js_alert(workflow_path: str):
    """
    Hiển thị alert JavaScript gốc kèm cảnh báo workflow selfhost.

    Args:
        workflow_path: Đường dẫn workflow để hiển thị trong alert
    """
    # Lấy URL ComfyUI từ config
    comfyui_config = config_manager.get_comfyui_config()
    comfyui_url = comfyui_config.get("comfyui_url", "http://localhost:8188")

    # Xây thông điệp alert
    title = tr("selfhost.warning.title")
    message = tr("selfhost.warning.message",
                 comfyui_url=comfyui_url,
                 workflow_path=f"workflows/{workflow_path}")
    hint = tr("selfhost.warning.hint")

    # Dọn định dạng markdown cho alert dạng plain text
    # Xoá ** (đậm) và các ký tự markdown khác
    message = message.replace("**", "").replace("*", "")
    hint = hint.replace("**", "").replace("*", "")

    # Gộp thành một thông điệp alert
    full_message = f"{title}\\n\\n{message}\\n\\n{hint}"

    # Escape cho chuỗi JavaScript
    full_message = full_message.replace("'", "\\'").replace('"', '\\"')
    full_message = full_message.replace("\n", "\\n")

    # Inject alert JavaScript
    js_code = f"""
    <script>
        alert("{full_message}");
    </script>
    """

    components.html(js_code, height=0, width=0)

