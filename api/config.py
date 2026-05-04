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
Cấu hình API
"""

from typing import Optional
from pydantic import BaseModel


class APIConfig(BaseModel):
    """Cấu hình API"""

    # Cấu hình server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = False

    # Cấu hình CORS
    cors_enabled: bool = True
    cors_origins: list[str] = ["*"]

    # Cấu hình task
    max_concurrent_tasks: int = 5
    task_cleanup_interval: int = 3600  # Dọn dẹp task hoàn thành mỗi giờ
    task_retention_time: int = 86400   # Giữ kết quả task trong 24 giờ

    # Cấu hình tải file
    max_upload_size: int = 100 * 1024 * 1024  # 100MB

    # Cấu hình API
    api_prefix: str = "/api"
    docs_url: Optional[str] = "/docs"
    redoc_url: Optional[str] = "/redoc"
    openapi_url: Optional[str] = "/openapi.json"


# Instance cấu hình toàn cục
api_config = APIConfig()

