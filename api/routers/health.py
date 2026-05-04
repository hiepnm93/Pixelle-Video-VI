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
Endpoint health check và thông tin hệ thống
"""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Phản hồi health check"""
    status: str = "healthy"
    version: str = "0.1.0"
    service: str = "Pixelle-Video API"


class CapabilitiesResponse(BaseModel):
    """Phản hồi capabilities"""
    success: bool = True
    capabilities: dict


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Endpoint health check

    Trả về trạng thái dịch vụ và thông tin phiên bản.
    """
    return HealthResponse()


@router.get("/version", response_model=HealthResponse)
async def get_version():
    """
    Lấy phiên bản API

    Trả về thông tin phiên bản.
    """
    return HealthResponse()

