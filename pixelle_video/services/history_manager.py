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
Service quản lý lịch sử (History Manager)

Logic nghiệp vụ cho quản lý lịch sử (không phụ thuộc UI).
Cung cấp các thao tác cấp cao trên nền PersistenceService.
"""

from typing import List, Dict, Optional, Any
from pathlib import Path
from loguru import logger

from pixelle_video.services.persistence import PersistenceService


class HistoryManager:
    """
    Service quản lý lịch sử

    Cung cấp logic nghiệp vụ cho:
    - Liệt kê và lọc các task
    - Lấy chi tiết task
    - Nhân bản task (để tạo lại)
    - Xóa task
    - Trong tương lai: Tạo lại frame, xuất file, v.v.
    """

    def __init__(self, persistence: PersistenceService):
        """
        Khởi tạo history manager

        Args:
            persistence: Instance của PersistenceService
        """
        self.persistence = persistence
    
    async def get_task_list(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Lấy danh sách task có phân trang

        Args:
            page: Số trang (bắt đầu từ 1)
            page_size: Số mục mỗi trang
            status: Lọc theo trạng thái (tùy chọn)
            sort_by: Trường để sắp xếp (created_at, completed_at, title, duration)
            sort_order: Thứ tự sắp xếp (asc, desc)

        Returns:
            {
                "tasks": [...],
                "total": 100,
                "page": 1,
                "page_size": 20,
                "total_pages": 5
            }
        """
        return await self.persistence.list_tasks_paginated(
            page=page,
            page_size=page_size,
            status=status,
            sort_by=sort_by,
            sort_order=sort_order
        )
    
    async def get_task_detail(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Lấy chi tiết đầy đủ của task, bao gồm cả storyboard

        Args:
            task_id: Task ID

        Returns:
            {
                "metadata": {...},      # Metadata của task
                "storyboard": {...}     # Dữ liệu storyboard (nếu có)
            }
            hoặc None nếu không tìm thấy task
        """
        metadata = await self.persistence.load_task_metadata(task_id)
        if not metadata:
            return None
        
        storyboard = await self.persistence.load_storyboard(task_id)
        
        return {
            "metadata": metadata,
            "storyboard": storyboard,
        }
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Lấy thống kê về tất cả các task

        Returns:
            {
                "total_tasks": 100,
                "completed": 95,
                "failed": 5,
                "total_duration": 3600.5,  # giây
                "total_size": 1024000000,  # byte
            }
        """
        return await self.persistence.get_statistics()
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Xóa một task và toàn bộ file của nó

        Args:
            task_id: Task ID cần xóa

        Returns:
            True nếu thành công, ngược lại False
        """
        return await self.persistence.delete_task(task_id)

    async def duplicate_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Nhân bản một task (lấy tham số input để tạo mới)

        Cho phép người dùng:
        1. Sao chép toàn bộ tham số tạo từ một task trước đó
        2. Điền sẵn vào form tạo
        3. Tạo lại với tham số giống/sửa đổi

        Args:
            task_id: Task ID cần nhân bản

        Returns:
            Dict tham số input hoặc None nếu không tìm thấy task
            {
                "text": "...",
                "mode": "generate",
                "title": "...",
                "n_scenes": 5,
                "tts_inference_mode": "local",
                "tts_voice": "...",
                ...
            }
        """
        metadata = await self.persistence.load_task_metadata(task_id)
        if not metadata:
            logger.warning(f"Không tìm thấy task {task_id} để nhân bản")
            return None

        # Trích xuất tham số input
        input_params = metadata.get("input", {})
        logger.info(f"Đã nhân bản tham số của task {task_id}")

        return input_params

    async def rebuild_index(self):
        """Xây dựng lại chỉ mục task (hữu ích khi bảo trì hoặc sau khi sửa thủ công)"""
        await self.persistence.rebuild_index()
    
    # ========================================================================
    # Mở rộng trong tương lai (Phase 3)
    # ========================================================================

    async def regenerate_frame(
        self,
        task_id: str,
        frame_index: int,
        **override_params
    ) -> Optional[str]:
        """
        Tạo lại một frame cụ thể (TÍNH NĂNG TƯƠNG LAI)

        Args:
            task_id: Task ID gốc
            frame_index: Index của frame cần tạo lại (bắt đầu từ 0)
            **override_params: Các tham số để ghi đè (image_prompt, style, v.v.)

        Returns:
            Đường dẫn ảnh frame mới hoặc None nếu thất bại

        TODO: Triển khai ở Phase 3
        - Tải storyboard gốc
        - Lấy các tham số của frame
        - Ghi đè bằng tham số mới
        - Gọi service tạo ảnh
        - Cập nhật storyboard
        - Compose lại video
        """
        logger.warning("regenerate_frame chưa được triển khai (tính năng Phase 3)")
        return None

    async def export_task(self, task_id: str, export_path: str) -> Optional[str]:
        """
        Xuất task thành một gói (metadata + video + frames) (TÍNH NĂNG TƯƠNG LAI)

        Args:
            task_id: Task ID cần xuất
            export_path: Đường dẫn file xuất (ví dụ: "exports/task.zip")

        Returns:
            Đường dẫn file đã xuất hoặc None nếu thất bại

        TODO: Triển khai ở Phase 3
        - Thu thập toàn bộ file của task
        - Tạo file nén ZIP
        - Bao gồm metadata.json, storyboard.json, video, frames
        """
        logger.warning("export_task chưa được triển khai (tính năng Phase 3)")
        return None

