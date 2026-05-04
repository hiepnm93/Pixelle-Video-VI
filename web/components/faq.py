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
Component FAQ để hiển thị các câu hỏi thường gặp
"""

import re
from pathlib import Path
from typing import Optional

import streamlit as st
from loguru import logger

from web.i18n import get_language, tr


def load_faq_content(language: str) -> Optional[str]:
    """
    Tải nội dung FAQ dựa trên ngôn ngữ hiện tại

    Args:
        language: Mã ngôn ngữ hiện tại (ví dụ: "zh_CN", "en_US")

    Returns:
        Nội dung FAQ dưới dạng markdown, hoặc None nếu không tìm thấy file
    """
    # Xác định file FAQ cần tải theo ngôn ngữ
    # Tiếng Trung (zh_CN) dùng FAQ_CN.md
    # Các ngôn ngữ khác dùng FAQ.md (tiếng Anh)
    project_root = Path(__file__).resolve().parent.parent.parent

    if language.startswith("zh"):
        faq_file = project_root / "docs" / "FAQ_CN.md"
    else:
        faq_file = project_root / "docs" / "FAQ.md"

    try:
        if faq_file.exists():
            with open(faq_file, "r", encoding="utf-8") as f:
                content = f.read()
            logger.debug(f"Đã tải FAQ từ: {faq_file}")
            return content
        else:
            logger.warning(f"Không tìm thấy file FAQ: {faq_file}")
            return None
    except Exception as e:
        logger.error(f"Không tải được file FAQ {faq_file}: {e}")
        return None


def parse_faq_sections(content: str) -> list[tuple[str, str]]:
    """
    Phân tích nội dung FAQ thành các mục theo tiêu đề ###

    Args:
        content: Nội dung markdown thô

    Returns:
        Danh sách các tuple (câu hỏi, câu trả lời)
    """
    # Bỏ tiêu đề chính đầu tiên (bắt đầu bằng #, không phải ###)
    lines = content.split('\n')
    if lines and lines[0].startswith('#') and not lines[0].startswith('##'):
        content = '\n'.join(lines[1:])

    # Tách theo các tiêu đề ### (câu hỏi cấp cao nhất)
    # Pattern khớp ### ở đầu dòng theo sau là phần text câu hỏi
    pattern = r'^###\s+(.+?)$'

    sections = []
    current_question = None
    current_answer_lines = []

    for line in content.split('\n'):
        match = re.match(pattern, line)
        if match:
            # Lưu mục trước đó nếu có
            if current_question is not None:
                answer = '\n'.join(current_answer_lines).strip()
                sections.append((current_question, answer))
            # Bắt đầu mục mới
            current_question = match.group(1).strip()
            current_answer_lines = []
        else:
            current_answer_lines.append(line)

    # Lưu mục cuối cùng
    if current_question is not None:
        answer = '\n'.join(current_answer_lines).strip()
        sections.append((current_question, answer))

    return sections


def render_faq_sidebar():
    """
    Render FAQ trong sidebar

    Component này hiển thị các câu hỏi thường gặp ở sidebar,
    giúp người dùng nhanh chóng tìm câu trả lời mà không cần rời khỏi giao diện chính.
    """
    with st.sidebar:
        # Tiêu đề FAQ kèm icon
        # st.markdown(f"### 🙋‍♀️ {tr('faq.title', fallback='FAQ')}")

        # Lấy ngôn ngữ hiện tại
        current_language = get_language()

        # Tải nội dung FAQ
        faq_content = load_faq_content(current_language)

        if faq_content:
            # Hiển thị FAQ trong một expander, mở sẵn theo mặc định
            with st.expander(tr('faq.expand_to_view', fallback='FAQ'), expanded=True):
                # Phân tích FAQ thành các mục
                sections = parse_faq_sections(faq_content)

                # Hiển thị từng câu hỏi trong expander có thể thu gọn riêng
                for question, answer in sections:
                    with st.expander(question, expanded=False):
                        st.markdown(answer, unsafe_allow_html=True)

            # Thêm liên kết đến GitHub issues để được trợ giúp thêm
            st.markdown(
                f"💡 {tr('faq.more_help', fallback='Cần trợ giúp thêm?')} "
                f"[GitHub Issues](https://github.com/AIDC-AI/Pixelle-Video/issues)"
            )
        else:
            # Nếu không tải được FAQ, chỉ hiển thị liên kết GitHub
            st.markdown(f"### 💡 {tr('faq.more_help', fallback='Cần trợ giúp?')}")
            st.markdown(
                f"[GitHub Issues](https://github.com/AIDC-AI/Pixelle-Video/issues) | "
                f"[Tài liệu](https://aidc-ai.github.io/Pixelle-Video)"
            )
