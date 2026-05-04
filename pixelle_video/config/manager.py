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
Configuration Manager - Mẫu Singleton

Cung cấp truy cập thống nhất tới cấu hình kèm xác thực tự động.
"""
from pathlib import Path
from typing import Any, Optional
from loguru import logger
from .schema import PixelleVideoConfig
from .loader import load_config_dict, save_config_dict


class ConfigManager:
    """
    Configuration Manager (Singleton)

    Cung cấp truy cập thống nhất tới cấu hình kèm xác thực tự động.
    """
    _instance: Optional['ConfigManager'] = None

    def __new__(cls, config_path: str = "config.yaml"):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, config_path: str = "config.yaml"):
        # Chỉ khởi tạo một lần
        if hasattr(self, '_initialized'):
            return

        self.config_path = Path(config_path)
        self.config: PixelleVideoConfig = self._load()
        self._initialized = True

    def _load(self) -> PixelleVideoConfig:
        """Nạp cấu hình từ file"""
        data = load_config_dict(str(self.config_path))
        config = PixelleVideoConfig(**data)

        # Xác thực rằng đường dẫn template tồn tại
        self._validate_template(config.template.default_template)

        return config

    def _validate_template(self, template_path: str):
        """Xác thực rằng template đã cấu hình tồn tại"""
        from pixelle_video.utils.template_util import resolve_template_path

        try:
            # Thử phân giải đường dẫn template
            resolved_path = resolve_template_path(template_path)
            logger.debug(f"Xác thực template thành công: {template_path} -> {resolved_path}")
        except FileNotFoundError as e:
            logger.warning(
                f"Không tìm thấy template mặc định đã cấu hình '{template_path}'. "
                f"Sẽ dùng dự phòng '1080x1920/default.html' nếu cần. Lỗi: {e}"
            )

    def reload(self):
        """Nạp lại cấu hình từ file"""
        self.config = self._load()
        logger.info("Đã nạp lại cấu hình")

    def save(self):
        """Lưu cấu hình hiện tại ra file"""
        save_config_dict(self.config.to_dict(), str(self.config_path))

    def update(self, updates: dict):
        """
        Cập nhật cấu hình với giá trị mới

        Args:
            updates: Dictionary chứa các cập nhật (ví dụ: {"llm": {"api_key": "xxx"}})
        """
        current = self.config.to_dict()

        # Hợp nhất sâu (deep merge)
        def deep_merge(base: dict, updates: dict) -> dict:
            for key, value in updates.items():
                if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                    deep_merge(base[key], value)
                else:
                    base[key] = value
            return base

        merged = deep_merge(current, updates)
        self.config = PixelleVideoConfig(**merged)

    def get(self, key: str, default: Any = None) -> Any:
        """Truy cập kiểu dict (giữ tương thích ngược)"""
        return self.config.to_dict().get(key, default)

    def validate(self) -> bool:
        """Xác thực tính đầy đủ của cấu hình"""
        return self.config.validate_required()

    def get_llm_config(self) -> dict:
        """Lấy cấu hình LLM dạng dict"""
        return {
            "api_key": self.config.llm.api_key,
            "base_url": self.config.llm.base_url,
            "model": self.config.llm.model,
        }

    def set_llm_config(self, api_key: str, base_url: str, model: str):
        """Đặt cấu hình LLM"""
        self.update({
            "llm": {
                "api_key": api_key,
                "base_url": base_url,
                "model": model,
            }
        })

    def get_comfyui_config(self) -> dict:
        """Lấy cấu hình ComfyUI dạng dict"""
        return {
            "comfyui_url": self.config.comfyui.comfyui_url,
            "comfyui_api_key": self.config.comfyui.comfyui_api_key,
            "runninghub_api_key": self.config.comfyui.runninghub_api_key,
            "runninghub_concurrent_limit": self.config.comfyui.runninghub_concurrent_limit,
            "runninghub_instance_type": self.config.comfyui.runninghub_instance_type,
            "tts": {
                "default_workflow": self.config.comfyui.tts.default_workflow,
            },
            "image": {
                "default_workflow": self.config.comfyui.image.default_workflow,
                "prompt_prefix": self.config.comfyui.image.prompt_prefix,
            },
            "video": {
                "default_workflow": self.config.comfyui.video.default_workflow,
                "prompt_prefix": self.config.comfyui.video.prompt_prefix,
            }
        }

    def set_comfyui_config(
        self,
        comfyui_url: Optional[str] = None,
        comfyui_api_key: Optional[str] = None,
        runninghub_api_key: Optional[str] = None,
        runninghub_concurrent_limit: Optional[int] = None,
        runninghub_instance_type: Optional[str] = None
    ):
        """Đặt cấu hình ComfyUI toàn cục"""
        updates = {}
        if comfyui_url is not None:
            updates["comfyui_url"] = comfyui_url
        if comfyui_api_key is not None:
            updates["comfyui_api_key"] = comfyui_api_key
        if runninghub_api_key is not None:
            updates["runninghub_api_key"] = runninghub_api_key
        if runninghub_concurrent_limit is not None:
            updates["runninghub_concurrent_limit"] = runninghub_concurrent_limit
        if runninghub_instance_type is not None:
            # Chuỗi rỗng nghĩa là tắt (lưu thành None)
            updates["runninghub_instance_type"] = runninghub_instance_type if runninghub_instance_type else None

        if updates:
            self.update({"comfyui": updates})

