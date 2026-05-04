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
Hệ thống cấu hình Pixelle-Video

Quản lý cấu hình thống nhất với validation bằng Pydantic.

Cách dùng:
    from pixelle_video.config import config_manager

    # Truy cập config (an toàn về kiểu)
    api_key = config_manager.config.llm.api_key

    # Cập nhật config
    config_manager.update({"llm": {"api_key": "xxx"}})
    config_manager.save()

    # Xác thực
    if config_manager.validate():
        print("Config hợp lệ!")
"""
from .schema import PixelleVideoConfig, LLMConfig, ComfyUIConfig, TTSSubConfig, ImageSubConfig, VideoSubConfig
from .manager import ConfigManager
from .loader import load_config_dict, save_config_dict

# Instance singleton toàn cục
config_manager = ConfigManager()

__all__ = [
    "PixelleVideoConfig",
    "LLMConfig",
    "ComfyUIConfig",
    "TTSSubConfig",
    "ImageSubConfig",
    "VideoSubConfig",
    "ConfigManager",
    "config_manager",
    "load_config_dict",
    "save_config_dict",
]

