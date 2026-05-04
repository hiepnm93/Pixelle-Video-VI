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
Prompt chuyển đổi phong cách

Dùng để chuyển mô tả phong cách tuỳ chỉnh của người dùng thành prompt sinh ảnh.
"""


STYLE_CONVERSION_PROMPT = """Convert this style description into a detailed image generation prompt for Stable Diffusion/FLUX:

Style Description: {description}

Requirements:
- Focus on visual elements, colors, lighting, mood, atmosphere
- Be specific and detailed
- Use professional photography/art terminology
- Output ONLY the prompt in English (no explanations)
- Keep it under 100 words
- Use comma-separated descriptive phrases

Image Prompt:"""


def build_style_conversion_prompt(description: str) -> str:
    """
    Xây dựng prompt chuyển đổi phong cách

    Chuyển mô tả phong cách của người dùng (ở bất kỳ ngôn ngữ nào) sang prompt
    sinh ảnh tiếng Anh phù hợp cho các model Stable Diffusion/FLUX.

    Args:
        description: Mô tả phong cách của người dùng ở bất kỳ ngôn ngữ nào

    Returns:
        Prompt đã định dạng

    Ví dụ:
        >>> build_style_conversion_prompt("phong cách cyberpunk, đèn neon, cảm giác tương lai")
        # Trả về prompt sẽ chuyển thành: "cyberpunk style, neon lights, futuristic..."
    """
    return STYLE_CONVERSION_PROMPT.format(description=description)

