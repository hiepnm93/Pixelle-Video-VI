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
Pixelle-Video Web UI - Điểm khởi chạy chính

Đây là điểm khởi chạy cho ứng dụng Streamlit nhiều trang.
Sử dụng st.navigation để định nghĩa các trang và đặt trang mặc định là Home.
"""

import sys
from pathlib import Path

# Thêm thư mục gốc của project vào sys.path để import module
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st

# Cấu hình trang (phải là lệnh Streamlit đầu tiên)
st.set_page_config(
    page_title="Pixelle-Video - Trình tạo video AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)


def main():
    """Điểm khởi chạy chính với navigation"""
    # Định nghĩa các trang bằng st.Page
    home_page = st.Page(
        "pages/1_🎬_Home.py",
        title="Trang chủ",
        icon="🎬",
        default=True
    )

    history_page = st.Page(
        "pages/2_📚_History.py",
        title="Lịch sử",
        icon="📚"
    )

    # Thiết lập navigation và chạy
    pg = st.navigation([home_page, history_page])
    pg.run()


if __name__ == "__main__":
    main()
