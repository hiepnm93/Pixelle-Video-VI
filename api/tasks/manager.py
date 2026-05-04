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
Task Manager

Quản lý task trong bộ nhớ cho các job tạo video.
"""

import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from loguru import logger

from api.tasks.models import Task, TaskStatus, TaskType, TaskProgress
from api.config import api_config


class TaskManager:
    """
    Trình quản lý task xử lý các tác vụ tạo video bất đồng bộ

    Tính năng:
    - Lưu trữ trong bộ nhớ (có thể thay bằng Redis sau này)
    - Quản lý vòng đời task
    - Theo dõi tiến trình
    - Tự động dọn dẹp task cũ
    """

    def __init__(self):
        self._tasks: Dict[str, Task] = {}
        self._task_futures: Dict[str, asyncio.Task] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Khởi động task manager và lập lịch dọn dẹp"""
        if self._running:
            logger.warning("Task manager đã đang chạy")
            return

        self._running = True
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("✅ Task manager đã khởi động")

    async def stop(self):
        """Dừng task manager và huỷ tất cả task"""
        self._running = False

        # Huỷ task dọn dẹp
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        # Huỷ tất cả task đang chạy
        for task_id, future in self._task_futures.items():
            if not future.done():
                future.cancel()
                logger.info(f"Đã huỷ task: {task_id}")

        self._tasks.clear()
        self._task_futures.clear()
        logger.info("✅ Task manager đã dừng")

    def create_task(
        self,
        task_type: TaskType,
        request_params: Optional[dict] = None
    ) -> Task:
        """
        Tạo một task mới

        Args:
            task_type: Loại task
            request_params: Tham số request gốc

        Returns:
            Task vừa tạo
        """
        task_id = str(uuid.uuid4())
        task = Task(
            task_id=task_id,
            task_type=task_type,
            status=TaskStatus.PENDING,
            request_params=request_params,
        )

        self._tasks[task_id] = task
        logger.info(f"Đã tạo task {task_id} ({task_type})")
        return task

    async def execute_task(
        self,
        task_id: str,
        coro_func: Callable,
        *args,
        **kwargs
    ):
        """
        Thực thi task bất đồng bộ

        Args:
            task_id: ID của task
            coro_func: Hàm async cần thực thi
            *args: Tham số vị trí
            **kwargs: Tham số từ khoá
        """
        task = self._tasks.get(task_id)
        if not task:
            logger.error(f"Không tìm thấy task {task_id}")
            return

        # Tạo task async
        async def _execute():
            try:
                task.status = TaskStatus.RUNNING
                task.started_at = datetime.now()
                logger.info(f"Task {task_id} đã bắt đầu")

                # Thực thi công việc thực tế
                result = await coro_func(*args, **kwargs)

                # Cập nhật task với kết quả
                task.status = TaskStatus.COMPLETED
                task.result = result
                task.completed_at = datetime.now()
                logger.info(f"Task {task_id} đã hoàn thành")

            except Exception as e:
                task.status = TaskStatus.FAILED
                task.error = str(e)
                task.completed_at = datetime.now()
                logger.error(f"Task {task_id} thất bại: {e}")

        # Bắt đầu thực thi
        future = asyncio.create_task(_execute())
        self._task_futures[task_id] = future

    def get_task(self, task_id: str) -> Optional[Task]:
        """Lấy task theo ID"""
        return self._tasks.get(task_id)

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        limit: int = 100
    ) -> List[Task]:
        """
        Liệt kê task có thể lọc tuỳ chọn

        Args:
            status: Lọc theo trạng thái
            limit: Số task tối đa trả về

        Returns:
            Danh sách task
        """
        tasks = list(self._tasks.values())

        if status:
            tasks = [t for t in tasks if t.status == status]

        # Sắp xếp theo created_at giảm dần
        tasks.sort(key=lambda t: t.created_at, reverse=True)

        return tasks[:limit]

    def update_progress(
        self,
        task_id: str,
        current: int,
        total: int,
        message: str = ""
    ):
        """
        Cập nhật tiến trình task

        Args:
            task_id: ID của task
            current: Tiến trình hiện tại
            total: Tổng số bước
            message: Thông điệp tiến trình
        """
        task = self._tasks.get(task_id)
        if not task:
            return

        percentage = (current / total * 100) if total > 0 else 0
        task.progress = TaskProgress(
            current=current,
            total=total,
            percentage=percentage,
            message=message
        )

    def cancel_task(self, task_id: str) -> bool:
        """
        Huỷ một task đang chạy

        Args:
            task_id: ID của task

        Returns:
            True nếu đã huỷ, ngược lại False
        """
        task = self._tasks.get(task_id)
        if not task:
            return False

        # Huỷ future nếu đang chạy
        future = self._task_futures.get(task_id)
        if future and not future.done():
            future.cancel()

        # Cập nhật trạng thái task
        task.status = TaskStatus.CANCELLED
        task.completed_at = datetime.now()
        logger.info(f"Đã huỷ task {task_id}")
        return True

    async def _cleanup_loop(self):
        """Định kỳ dọn dẹp các task cũ đã hoàn thành"""
        while self._running:
            try:
                await asyncio.sleep(api_config.task_cleanup_interval)
                self._cleanup_old_tasks()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Lỗi trong vòng lặp dọn dẹp: {e}")

    def _cleanup_old_tasks(self):
        """Xoá các task cũ đã hoàn thành/thất bại"""
        cutoff_time = datetime.now() - timedelta(seconds=api_config.task_retention_time)

        tasks_to_remove = []
        for task_id, task in self._tasks.items():
            if task.status in [TaskStatus.COMPLETED, TaskStatus.FAILED, TaskStatus.CANCELLED]:
                if task.completed_at and task.completed_at < cutoff_time:
                    tasks_to_remove.append(task_id)

        for task_id in tasks_to_remove:
            del self._tasks[task_id]
            if task_id in self._task_futures:
                del self._task_futures[task_id]

        if tasks_to_remove:
            logger.info(f"Đã dọn dẹp {len(tasks_to_remove)} task cũ")


# Instance task manager toàn cục
task_manager = TaskManager()
