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
Bộ tải cấu hình - YAML thuần

Xử lý việc nạp và lưu cấu hình từ/đến file YAML.
"""
from pathlib import Path
import yaml
from loguru import logger


def load_config_dict(config_path: str = "config.yaml") -> dict:
    """
    Nạp cấu hình từ file YAML

    Args:
        config_path: Đường dẫn tới file config

    Returns:
        Dictionary cấu hình
    """
    config_file = Path(config_path)

    if not config_file.exists():
        logger.warning(f"Không tìm thấy file config: {config_path}")
        logger.info("Sử dụng cấu hình mặc định")
        return {}

    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f) or {}
        logger.info(f"Đã nạp cấu hình từ {config_path}")
        return data
    except Exception as e:
        logger.error(f"Không thể nạp config: {e}")
        return {}


def save_config_dict(config: dict, config_path: str = "config.yaml"):
    """
    Lưu cấu hình ra file YAML

    Args:
        config: Dictionary cấu hình
        config_path: Đường dẫn tới file config
    """
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
        logger.info(f"Đã lưu cấu hình tới {config_path}")
    except Exception as e:
        logger.error(f"Không thể lưu config: {e}")
        raise

