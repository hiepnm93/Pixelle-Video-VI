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
Các hàm hỗ trợ async cho web UI
"""

import asyncio
import tomllib
from pathlib import Path

from loguru import logger


def run_async(coro):
    """Chạy coroutine async trong ngữ cảnh đồng bộ"""
    return asyncio.run(coro)


def get_project_version():
    """Lấy phiên bản dự án từ pyproject.toml"""
    try:
        # Lấy thư mục gốc dự án (thư mục cha của web)
        web_dir = Path(__file__).resolve().parent.parent
        project_root = web_dir.parent
        pyproject_path = project_root / "pyproject.toml"

        if pyproject_path.exists():
            with open(pyproject_path, "rb") as f:
                pyproject_data = tomllib.load(f)
                return pyproject_data.get("project", {}).get("version", "Unknown")
    except Exception as e:
        logger.warning(f"Không đọc được phiên bản từ pyproject.toml: {e}")
    return "Unknown"

