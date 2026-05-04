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
Các hàm tiện ích LLM cho việc khám phá model và kiểm tra kết nối.

Dùng endpoint /v1/models tương thích chuẩn OpenAI.
"""

from typing import List, Tuple
import httpx
from loguru import logger


def fetch_available_models(api_key: str, base_url: str, timeout: float = 10.0) -> List[str]:
    """
    Lấy danh sách model có sẵn từ endpoint API tương thích OpenAI.

    Dùng endpoint chuẩn GET /v1/models với xác thực Bearer token.

    Args:
        api_key: API key để xác thực
        base_url: URL gốc của API (vd: https://api.openai.com/v1)
        timeout: Timeout request tính bằng giây

    Returns:
        Danh sách ID các model có sẵn từ API

    Raises:
        httpx.HTTPStatusError: Nếu API trả về mã lỗi
        httpx.RequestError: Nếu có lỗi mạng
    """
    # Chuẩn hoá base_url - đảm bảo kết thúc bằng /v1 hoặc tương tự
    base_url = base_url.rstrip("/")

    # Xây dựng URL endpoint models
    # Xử lý trường hợp base_url có thể có hoặc không có /v1
    if base_url.endswith("/v1"):
        models_url = f"{base_url}/models"
    else:
        models_url = f"{base_url}/v1/models"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    logger.debug(f"Đang lấy danh sách model từ: {models_url}")

    with httpx.Client(timeout=timeout) as client:
        response = client.get(models_url, headers=headers)
        response.raise_for_status()

        data = response.json()
        models = [model["id"] for model in data.get("data", [])]

        # Sắp xếp model theo bảng chữ cái cho UX tốt hơn
        models.sort()

        logger.debug(f"Đã lấy được {len(models)} model")
        return models


def test_llm_connection(api_key: str, base_url: str, timeout: float = 10.0) -> Tuple[bool, str, int]:
    """
    Kiểm tra kết nối LLM API bằng cách thử lấy danh sách model.

    Args:
        api_key: API key để xác thực
        base_url: URL gốc của API
        timeout: Timeout request tính bằng giây

    Returns:
        Tuple (success: bool, message: str, model_count: int)
        - success: True nếu kết nối thành công
        - message: Thông báo trạng thái dạng văn bản
        - model_count: Số model có sẵn (0 nếu thất bại)
    """
    try:
        models = fetch_available_models(api_key, base_url, timeout)
        return True, f"Kết nối thành công! Có sẵn {len(models)} model.", len(models)
    except httpx.HTTPStatusError as e:
        status_code = e.response.status_code
        if status_code == 401:
            return False, "Xác thực thất bại: API Key không hợp lệ", 0
        elif status_code == 403:
            return False, "Truy cập bị từ chối: Kiểm tra quyền của API Key", 0
        elif status_code == 404:
            return False, "Không tìm thấy endpoint API: Kiểm tra Base URL của bạn", 0
        else:
            return False, f"Lỗi API: HTTP {status_code}", 0
    except httpx.ConnectError:
        return False, "Kết nối thất bại: Không thể kết nối tới server", 0
    except httpx.TimeoutException:
        return False, "Timeout kết nối: Server không phản hồi kịp thời", 0
    except Exception as e:
        logger.error(f"Lỗi kiểm tra kết nối LLM: {e}")
        return False, f"Lỗi: {str(e)}", 0
