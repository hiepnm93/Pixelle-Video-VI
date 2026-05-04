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
Các schema cho API khám phá tài nguyên
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class WorkflowInfo(BaseModel):
    """Thông tin workflow"""
    name: str = Field(..., description="Tên file workflow")
    display_name: str = Field(..., description="Tên hiển thị kèm thông tin nguồn")
    source: str = Field(..., description="Nguồn (runninghub hoặc selfhost)")
    path: str = Field(..., description="Đường dẫn đầy đủ tới file workflow")
    key: str = Field(..., description="Khoá workflow (source/name)")
    workflow_id: Optional[str] = Field(None, description="ID workflow của RunningHub (nếu có)")


class WorkflowListResponse(BaseModel):
    """Phản hồi danh sách workflow"""
    success: bool = True
    message: str = "Success"
    workflows: List[WorkflowInfo] = Field(..., description="Danh sách workflow có sẵn")


class TemplateInfo(BaseModel):
    """Thông tin template"""
    name: str = Field(..., description="Tên file template")
    display_name: str = Field(..., description="Tên hiển thị")
    size: str = Field(..., description="Kích thước (ví dụ: 1080x1920)")
    width: int = Field(..., description="Chiều rộng tính bằng pixel")
    height: int = Field(..., description="Chiều cao tính bằng pixel")
    orientation: str = Field(..., description="Hướng (portrait/landscape/square)")
    path: str = Field(..., description="Đường dẫn đầy đủ tới file template")
    key: str = Field(..., description="Khoá template (size/name)")


class TemplateListResponse(BaseModel):
    """Phản hồi danh sách template"""
    success: bool = True
    message: str = "Success"
    templates: List[TemplateInfo] = Field(..., description="Danh sách template có sẵn")


class BGMInfo(BaseModel):
    """Thông tin BGM"""
    name: str = Field(..., description="Tên file BGM")
    path: str = Field(..., description="Đường dẫn đầy đủ tới file BGM")
    source: str = Field(..., description="Nguồn (default hoặc custom)")


class BGMListResponse(BaseModel):
    """Phản hồi danh sách BGM"""
    success: bool = True
    message: str = "Success"
    bgm_files: List[BGMInfo] = Field(..., description="Danh sách file BGM có sẵn")
