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
Package Prompts

Quản lý tập trung tất cả prompt cho mọi tương tác với LLM.
"""

# Prompts cho thuyết minh
from pixelle_video.prompts.topic_narration import build_topic_narration_prompt
from pixelle_video.prompts.content_narration import build_content_narration_prompt
from pixelle_video.prompts.title_generation import build_title_generation_prompt

# Prompts cho ảnh
from pixelle_video.prompts.image_generation import (
    build_image_prompt_prompt,
    IMAGE_STYLE_PRESETS,
    DEFAULT_IMAGE_STYLE
)
from pixelle_video.prompts.style_conversion import build_style_conversion_prompt


__all__ = [
    # Builder cho thuyết minh
    "build_topic_narration_prompt",
    "build_content_narration_prompt",
    "build_title_generation_prompt",

    # Builder cho ảnh
    "build_image_prompt_prompt",
    "build_style_conversion_prompt",

    # Preset phong cách ảnh
    "IMAGE_STYLE_PRESETS",
    "DEFAULT_IMAGE_STYLE",
]
