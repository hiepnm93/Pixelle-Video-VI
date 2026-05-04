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
Các endpoint quản lý task

Endpoint dùng để quản lý các task bất đồng bộ (kiểm tra trạng thái, huỷ, v.v.)
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from loguru import logger

from api.tasks import task_manager, Task, TaskStatus

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.get("", response_model=List[Task])
async def list_tasks(
    status: Optional[TaskStatus] = Query(None, description="Lọc theo trạng thái"),
    limit: int = Query(100, ge=1, le=1000, description="Số lượng task tối đa")
):
    """
    Liệt kê các task

    Lấy danh sách task có thể lọc tuỳ chọn.

    - **status**: Lọc theo trạng thái (pending/running/completed/failed/cancelled)
    - **limit**: Số lượng task tối đa trả về (mặc định 100)

    Trả về danh sách task được sắp xếp theo thời gian tạo (mới nhất trước).
    """
    try:
        tasks = task_manager.list_tasks(status=status, limit=limit)
        return tasks

    except Exception as e:
        logger.error(f"Lỗi liệt kê task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=Task)
async def get_task(task_id: str):
    """
    Lấy chi tiết task

    Lấy thông tin chi tiết về một task cụ thể.

    - **task_id**: ID của task

    Trả về chi tiết task gồm trạng thái, tiến trình và kết quả (nếu đã hoàn thành).
    """
    try:
        task = task_manager.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy task {task_id}")

        return task

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi lấy task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}")
async def cancel_task(task_id: str):
    """
    Huỷ task

    Huỷ một task đang chạy hoặc đang chờ.

    - **task_id**: ID của task

    Trả về trạng thái thành công.
    """
    try:
        success = task_manager.cancel_task(task_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Không tìm thấy task {task_id}")

        return {
            "success": True,
            "message": f"Đã huỷ task {task_id} thành công"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi huỷ task: {e}")
        raise HTTPException(status_code=500, detail=str(e))
