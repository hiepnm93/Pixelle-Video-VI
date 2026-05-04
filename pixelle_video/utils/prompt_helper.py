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
Tiện ích helper cho prompt

Các tiện ích đơn giản để xây dựng prompt với tiền tố tuỳ chọn.
"""


def build_image_prompt(prompt: str, prefix: str = "") -> str:
    """
    Xây dựng prompt ảnh cuối cùng kèm tiền tố tuỳ chọn

    Args:
        prompt: Prompt thô của người dùng
        prefix: Tiền tố tuỳ chọn để thêm trước prompt

    Returns:
        Prompt cuối cùng kèm tiền tố (nếu có)

    Ví dụ:
        >>> build_image_prompt("a cat", "")
        'a cat'

        >>> build_image_prompt("a cat", "anime style")
        'anime style, a cat'

        >>> build_image_prompt("a cat", "  anime style  ")
        'anime style, a cat'
    """
    prefix = prefix.strip() if prefix else ""
    prompt = prompt.strip() if prompt else ""

    if prefix and prompt:
        return f"{prefix}, {prompt}"
    elif prefix:
        return prefix
    else:
        return prompt

