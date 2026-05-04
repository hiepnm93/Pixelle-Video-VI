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
Service Persistence

Xử lý lưu trữ metadata task và storyboard vào filesystem.
"""

import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime
from loguru import logger

from pixelle_video.models.storyboard import Storyboard, StoryboardFrame, StoryboardConfig, ContentMetadata


class PersistenceService:
    """
    Service persistence cho task dùng filesystem (JSON)

    Cấu trúc file:
        output/
        └── {task_id}/
            ├── metadata.json          # Metadata task (input, kết quả, config)
            ├── storyboard.json        # Dữ liệu storyboard (frame, prompt)
            ├── final.mp4
            └── frames/
                ├── 01_audio.mp3
                ├── 01_image.png
                └── ...

    Cách dùng:
        persistence = PersistenceService()

        # Lưu metadata
        await persistence.save_task_metadata(task_id, metadata)

        # Lưu storyboard
        await persistence.save_storyboard(task_id, storyboard)

        # Nạp task
        metadata = await persistence.load_task_metadata(task_id)
        storyboard = await persistence.load_storyboard(task_id)

        # Liệt kê tất cả task
        tasks = await persistence.list_tasks(status="completed", limit=50)
    """
    
    def __init__(self, output_dir: str = "output"):
        """
        Khởi tạo service persistence

        Args:
            output_dir: Thư mục output gốc (mặc định: "output")
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # File index để liệt kê nhanh
        self.index_file = self.output_dir / ".index.json"
        self._ensure_index()

    def get_task_dir(self, task_id: str) -> Path:
        """Lấy đường dẫn thư mục task"""
        return self.output_dir / task_id

    def get_metadata_path(self, task_id: str) -> Path:
        """Lấy đường dẫn metadata.json"""
        return self.get_task_dir(task_id) / "metadata.json"

    def get_storyboard_path(self, task_id: str) -> Path:
        """Lấy đường dẫn storyboard.json"""
        return self.get_task_dir(task_id) / "storyboard.json"
    
    # ========================================================================
    # Metadata Operations
    # ========================================================================
    
    async def save_task_metadata(
        self,
        task_id: str,
        metadata: Dict[str, Any]
    ):
        """
        Lưu metadata task vào filesystem

        Args:
            task_id: Task ID
            metadata: Dict metadata có cấu trúc:
                {
                    "task_id": str,
                    "created_at": str,
                    "completed_at": str (tuỳ chọn),
                    "status": str,
                    "input": dict,
                    "result": dict (tuỳ chọn),
                    "config": dict
                }
        """
        try:
            task_dir = self.get_task_dir(task_id)
            task_dir.mkdir(parents=True, exist_ok=True)

            metadata_path = self.get_metadata_path(task_id)

            # Đảm bảo task_id được đặt
            metadata["task_id"] = task_id

            # Chuyển object datetime thành chuỗi ISO
            if "created_at" in metadata and isinstance(metadata["created_at"], datetime):
                metadata["created_at"] = metadata["created_at"].isoformat()
            if "completed_at" in metadata and isinstance(metadata["completed_at"], datetime):
                metadata["completed_at"] = metadata["completed_at"].isoformat()

            with open(metadata_path, "w", encoding="utf-8") as f:
                json.dump(metadata, f, indent=2, ensure_ascii=False)

            logger.debug(f"Đã lưu metadata task: {task_id}")

            # Cập nhật index
            await self._update_index_for_task(task_id, metadata)

        except Exception as e:
            logger.error(f"Không thể lưu metadata task {task_id}: {e}")
            raise

    async def load_task_metadata(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Nạp metadata task từ filesystem

        Args:
            task_id: Task ID

        Returns:
            Dict metadata hoặc None nếu không tìm thấy
        """
        try:
            metadata_path = self.get_metadata_path(task_id)

            if not metadata_path.exists():
                return None

            with open(metadata_path, "r", encoding="utf-8") as f:
                metadata = json.load(f)

            return metadata

        except Exception as e:
            logger.error(f"Không thể nạp metadata task {task_id}: {e}")
            return None

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        error: Optional[str] = None
    ):
        """
        Cập nhật trạng thái task trong metadata

        Args:
            task_id: Task ID
            status: Trạng thái mới (pending, running, completed, failed, cancelled)
            error: Thông báo lỗi (tuỳ chọn, dùng cho trạng thái failed)
        """
        try:
            metadata = await self.load_task_metadata(task_id)
            if not metadata:
                logger.warning(f"Không thể cập nhật trạng thái: không tìm thấy task {task_id}")
                return

            metadata["status"] = status

            if status in ["completed", "failed", "cancelled"]:
                metadata["completed_at"] = datetime.now().isoformat()

            if error:
                metadata["error"] = error

            await self.save_task_metadata(task_id, metadata)

        except Exception as e:
            logger.error(f"Không thể cập nhật trạng thái task {task_id}: {e}")
    
    # ========================================================================
    # Storyboard Operations
    # ========================================================================
    
    async def save_storyboard(
        self,
        task_id: str,
        storyboard: Storyboard
    ):
        """
        Lưu storyboard vào filesystem

        Args:
            task_id: Task ID
            storyboard: Instance Storyboard
        """
        try:
            task_dir = self.get_task_dir(task_id)
            task_dir.mkdir(parents=True, exist_ok=True)

            storyboard_path = self.get_storyboard_path(task_id)

            # Chuyển storyboard sang dict
            storyboard_dict = self._storyboard_to_dict(storyboard)

            with open(storyboard_path, "w", encoding="utf-8") as f:
                json.dump(storyboard_dict, f, indent=2, ensure_ascii=False)

            logger.debug(f"Đã lưu storyboard: {task_id}")

        except Exception as e:
            logger.error(f"Không thể lưu storyboard {task_id}: {e}")
            raise

    async def load_storyboard(self, task_id: str) -> Optional[Storyboard]:
        """
        Nạp storyboard từ filesystem

        Args:
            task_id: Task ID

        Returns:
            Instance Storyboard hoặc None nếu không tìm thấy
        """
        try:
            storyboard_path = self.get_storyboard_path(task_id)

            if not storyboard_path.exists():
                return None

            with open(storyboard_path, "r", encoding="utf-8") as f:
                storyboard_dict = json.load(f)

            # Chuyển dict thành storyboard
            storyboard = self._dict_to_storyboard(storyboard_dict)

            return storyboard

        except Exception as e:
            logger.error(f"Không thể nạp storyboard {task_id}: {e}")
            return None
    
    # ========================================================================
    # Task Listing & Querying
    # ========================================================================
    
    async def list_tasks(
        self,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Liệt kê task với lọc tuỳ chọn

        Args:
            status: Lọc theo trạng thái (pending, running, completed, failed, cancelled)
            limit: Số task tối đa trả về
            offset: Số task bỏ qua

        Returns:
            Danh sách dict metadata, sắp xếp theo created_at giảm dần
        """
        try:
            tasks = []

            # Quét tất cả thư mục task
            for task_dir in self.output_dir.iterdir():
                if not task_dir.is_dir():
                    continue

                metadata_path = task_dir / "metadata.json"
                if not metadata_path.exists():
                    continue

                try:
                    with open(metadata_path, "r", encoding="utf-8") as f:
                        metadata = json.load(f)

                    # Lọc theo trạng thái
                    if status and metadata.get("status") != status:
                        continue

                    tasks.append(metadata)

                except Exception as e:
                    logger.warning(f"Không thể nạp metadata từ {task_dir}: {e}")
                    continue

            # Sắp xếp theo created_at giảm dần
            tasks.sort(key=lambda t: t.get("created_at", ""), reverse=True)

            # Áp dụng phân trang
            return tasks[offset:offset + limit]

        except Exception as e:
            logger.error(f"Không thể liệt kê task: {e}")
            return []

    async def task_exists(self, task_id: str) -> bool:
        """Kiểm tra task có tồn tại không"""
        return self.get_task_dir(task_id).exists()

    async def delete_task(self, task_id: str):
        """
        Xoá thư mục task và tất cả file

        Args:
            task_id: Task ID
        """
        try:
            task_dir = self.get_task_dir(task_id)

            if task_dir.exists():
                import shutil
                shutil.rmtree(task_dir)
                logger.info(f"Đã xoá task: {task_id}")

        except Exception as e:
            logger.error(f"Không thể xoá task {task_id}: {e}")
            raise
    
    # ========================================================================
    # Serialization Helpers
    # ========================================================================
    
    def _storyboard_to_dict(self, storyboard: Storyboard) -> Dict[str, Any]:
        """Chuyển Storyboard sang dict để serialize JSON"""
        return {
            "title": storyboard.title,
            "config": self._config_to_dict(storyboard.config),
            "frames": [self._frame_to_dict(frame) for frame in storyboard.frames],
            "content_metadata": self._content_metadata_to_dict(storyboard.content_metadata) if storyboard.content_metadata else None,
            "final_video_path": storyboard.final_video_path,
            "total_duration": storyboard.total_duration,
            "created_at": storyboard.created_at.isoformat() if storyboard.created_at else None,
            "completed_at": storyboard.completed_at.isoformat() if storyboard.completed_at else None,
        }
    
    def _dict_to_storyboard(self, data: Dict[str, Any]) -> Storyboard:
        """Chuyển dict thành instance Storyboard"""
        return Storyboard(
            title=data["title"],
            config=self._dict_to_config(data["config"]),
            frames=[self._dict_to_frame(frame_data) for frame_data in data["frames"]],
            content_metadata=self._dict_to_content_metadata(data["content_metadata"]) if data.get("content_metadata") else None,
            final_video_path=data.get("final_video_path"),
            total_duration=data.get("total_duration", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
            completed_at=datetime.fromisoformat(data["completed_at"]) if data.get("completed_at") else None,
        )
    
    def _config_to_dict(self, config: StoryboardConfig) -> Dict[str, Any]:
        """Chuyển StoryboardConfig sang dict"""
        return {
            "task_id": config.task_id,
            "n_storyboard": config.n_storyboard,
            "min_narration_words": config.min_narration_words,
            "max_narration_words": config.max_narration_words,
            "min_image_prompt_words": config.min_image_prompt_words,
            "max_image_prompt_words": config.max_image_prompt_words,
            "video_fps": config.video_fps,
            "tts_inference_mode": config.tts_inference_mode,
            "voice_id": config.voice_id,
            "tts_workflow": config.tts_workflow,
            "tts_speed": config.tts_speed,
            "ref_audio": config.ref_audio,
            "media_width": config.media_width,
            "media_height": config.media_height,
            "media_workflow": config.media_workflow,
            "frame_template": config.frame_template,
            "template_params": config.template_params,
        }
    
    def _dict_to_config(self, data: Dict[str, Any]) -> StoryboardConfig:
        """Chuyển dict sang StoryboardConfig"""
        return StoryboardConfig(
            task_id=data.get("task_id"),
            n_storyboard=data.get("n_storyboard", 5),
            min_narration_words=data.get("min_narration_words", 5),
            max_narration_words=data.get("max_narration_words", 20),
            min_image_prompt_words=data.get("min_image_prompt_words", 30),
            max_image_prompt_words=data.get("max_image_prompt_words", 60),
            video_fps=data.get("video_fps", 30),
            tts_inference_mode=data.get("tts_inference_mode", "local"),
            voice_id=data.get("voice_id"),
            tts_workflow=data.get("tts_workflow"),
            tts_speed=data.get("tts_speed"),
            ref_audio=data.get("ref_audio"),
            media_width=data.get("media_width", data.get("image_width", 1024)),  # Tương thích ngược
            media_height=data.get("media_height", data.get("image_height", 1024)),  # Tương thích ngược
            media_workflow=data.get("media_workflow", data.get("image_workflow")),  # Tương thích ngược
            frame_template=data.get("frame_template", "1080x1920/default.html"),
            template_params=data.get("template_params"),
        )
    
    def _frame_to_dict(self, frame: StoryboardFrame) -> Dict[str, Any]:
        """Chuyển StoryboardFrame sang dict"""
        return {
            "index": frame.index,
            "narration": frame.narration,
            "image_prompt": frame.image_prompt,
            "audio_path": frame.audio_path,
            "media_type": frame.media_type,
            "image_path": frame.image_path,
            "video_path": frame.video_path,
            "composed_image_path": frame.composed_image_path,
            "video_segment_path": frame.video_segment_path,
            "duration": frame.duration,
            "created_at": frame.created_at.isoformat() if frame.created_at else None,
        }
    
    def _dict_to_frame(self, data: Dict[str, Any]) -> StoryboardFrame:
        """Chuyển dict sang StoryboardFrame"""
        return StoryboardFrame(
            index=data["index"],
            narration=data["narration"],
            image_prompt=data["image_prompt"],
            audio_path=data.get("audio_path"),
            media_type=data.get("media_type"),
            image_path=data.get("image_path"),
            video_path=data.get("video_path"),
            composed_image_path=data.get("composed_image_path"),
            video_segment_path=data.get("video_segment_path"),
            duration=data.get("duration", 0.0),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None,
        )
    
    def _content_metadata_to_dict(self, metadata: ContentMetadata) -> Dict[str, Any]:
        """Chuyển ContentMetadata sang dict"""
        return {
            "title": metadata.title,
            "author": metadata.author,
            "subtitle": metadata.subtitle,
            "genre": metadata.genre,
            "summary": metadata.summary,
            "publication_year": metadata.publication_year,
            "cover_url": metadata.cover_url,
        }
    
    def _dict_to_content_metadata(self, data: Dict[str, Any]) -> ContentMetadata:
        """Chuyển dict sang ContentMetadata"""
        return ContentMetadata(
            title=data["title"],
            author=data.get("author"),
            subtitle=data.get("subtitle"),
            genre=data.get("genre"),
            summary=data.get("summary"),
            publication_year=data.get("publication_year"),
            cover_url=data.get("cover_url"),
        )
    
    # ========================================================================
    # Index Management (for fast listing)
    # ========================================================================
    
    def _ensure_index(self):
        """Đảm bảo file index tồn tại, tạo nếu chưa có"""
        if not self.index_file.exists():
            self._save_index({"version": "1.0", "tasks": []})

    def _load_index(self) -> Dict[str, Any]:
        """Nạp index từ file"""
        try:
            with open(self.index_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Không thể nạp index: {e}")
            return {"version": "1.0", "tasks": []}

    def _save_index(self, index_data: Dict[str, Any]):
        """Lưu index ra file"""
        try:
            index_data["last_updated"] = datetime.now().isoformat()
            with open(self.index_file, "w", encoding="utf-8") as f:
                json.dump(index_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Không thể lưu index: {e}")

    async def _update_index_for_task(self, task_id: str, metadata: Dict[str, Any]):
        """Cập nhật entry index cho một task cụ thể"""
        index = self._load_index()

        # Thử lấy tiêu đề từ nhiều nguồn
        title = metadata.get("input", {}).get("title")
        if not title or title == "":
            # Thử lấy tiêu đề từ storyboard nếu tiêu đề input rỗng
            storyboard = await self.load_storyboard(task_id)
            if storyboard and storyboard.title:
                title = storyboard.title
            else:
                # Dự phòng: dùng preview của text input
                input_text = metadata.get("input", {}).get("text", "")
                if input_text:
                    # Dùng 30 ký tự đầu của text input làm tiêu đề
                    title = input_text[:30] + ("..." if len(input_text) > 30 else "")
                else:
                    title = "Không có tiêu đề"
        
        # Trích xuất thông tin chính cho index
        index_entry = {
            "task_id": task_id,
            "created_at": metadata.get("created_at"),
            "completed_at": metadata.get("completed_at"),
            "status": metadata.get("status", "unknown"),
            "title": title,
            "duration": metadata.get("result", {}).get("duration", 0),
            "n_frames": metadata.get("result", {}).get("n_frames", 0),
            "file_size": metadata.get("result", {}).get("file_size", 0),
            "video_path": metadata.get("result", {}).get("video_path"),
        }

        # Cập nhật hoặc thêm
        tasks = index.get("tasks", [])
        existing_idx = next((i for i, t in enumerate(tasks) if t["task_id"] == task_id), None)

        if existing_idx is not None:
            tasks[existing_idx] = index_entry
        else:
            tasks.append(index_entry)

        index["tasks"] = tasks
        self._save_index(index)

    async def rebuild_index(self):
        """Xây dựng lại index bằng cách quét tất cả thư mục task"""
        logger.info("Đang xây dựng lại index task...")
        index = {"version": "1.0", "tasks": []}

        # Quét tất cả thư mục
        for task_dir in self.output_dir.iterdir():
            if not task_dir.is_dir() or task_dir.name.startswith("."):
                continue

            task_id = task_dir.name
            metadata = await self.load_task_metadata(task_id)

            if metadata:
                # Thử lấy tiêu đề từ nhiều nguồn
                title = metadata.get("input", {}).get("title")
                if not title or title == "":
                    # Thử lấy tiêu đề từ storyboard nếu tiêu đề input rỗng
                    storyboard = await self.load_storyboard(task_id)
                    if storyboard and storyboard.title:
                        title = storyboard.title
                    else:
                        # Dự phòng: dùng preview của text input
                        input_text = metadata.get("input", {}).get("text", "")
                        if input_text:
                            # Dùng 30 ký tự đầu của text input làm tiêu đề
                            title = input_text[:30] + ("..." if len(input_text) > 30 else "")
                        else:
                            title = "Không có tiêu đề"

                # Thêm vào index
                index["tasks"].append({
                    "task_id": task_id,
                    "created_at": metadata.get("created_at"),
                    "completed_at": metadata.get("completed_at"),
                    "status": metadata.get("status", "unknown"),
                    "title": title,
                    "duration": metadata.get("result", {}).get("duration", 0),
                    "n_frames": metadata.get("result", {}).get("n_frames", 0),
                    "file_size": metadata.get("result", {}).get("file_size", 0),
                    "video_path": metadata.get("result", {}).get("video_path"),
                })
        
        self._save_index(index)
        logger.info(f"Đã xây dựng lại index: {len(index['tasks'])} task")
    
    # ========================================================================
    # Paginated Listing
    # ========================================================================
    
    async def list_tasks_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Dict[str, Any]:
        """
        Liệt kê task có phân trang

        Args:
            page: Số trang (đếm từ 1)
            page_size: Số task mỗi trang
            status: Lọc theo trạng thái (tuỳ chọn)
            sort_by: Trường sắp xếp (created_at, completed_at, title, duration)
            sort_order: Thứ tự sắp xếp (asc, desc)

        Returns:
            {
                "tasks": [...],          # Danh sách tóm tắt task
                "total": 100,            # Tổng số task khớp
                "page": 1,               # Trang hiện tại
                "page_size": 20,         # Số task mỗi trang
                "total_pages": 5         # Tổng số trang
            }
        """
        index = self._load_index()
        tasks = index.get("tasks", [])

        # Lọc theo trạng thái
        if status:
            tasks = [t for t in tasks if t.get("status") == status]

        # Sắp xếp
        reverse = (sort_order == "desc")
        if sort_by in ["created_at", "completed_at"]:
            tasks.sort(
                key=lambda t: datetime.fromisoformat(t.get(sort_by, "1970-01-01T00:00:00")),
                reverse=reverse
            )
        elif sort_by in ["title", "duration", "n_frames"]:
            tasks.sort(key=lambda t: t.get(sort_by, ""), reverse=reverse)

        # Phân trang
        total = len(tasks)
        total_pages = (total + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        page_tasks = tasks[start_idx:end_idx]
        
        return {
            "tasks": page_tasks,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages,
        }
    
    # ========================================================================
    # Statistics
    # ========================================================================
    
    async def get_statistics(self) -> Dict[str, Any]:
        """
        Lấy thống kê về tất cả task

        Returns:
            {
                "total_tasks": 100,
                "completed": 95,
                "failed": 5,
                "total_duration": 3600.5,  # giây
                "total_size": 1024000000,  # byte
            }
        """
        index = self._load_index()
        tasks = index.get("tasks", [])
        
        stats = {
            "total_tasks": len(tasks),
            "completed": len([t for t in tasks if t.get("status") == "completed"]),
            "failed": len([t for t in tasks if t.get("status") == "failed"]),
            "total_duration": sum(t.get("duration", 0) for t in tasks),
            "total_size": sum(t.get("file_size", 0) for t in tasks),
        }
        
        return stats
    
    # ========================================================================
    # Delete Task
    # ========================================================================
    
    async def delete_task(self, task_id: str) -> bool:
        """
        Xoá một task và tất cả file của nó

        Args:
            task_id: Task ID cần xoá

        Returns:
            True nếu thành công, False nếu thất bại
        """
        try:
            import shutil

            task_dir = self.get_task_dir(task_id)
            if task_dir.exists():
                shutil.rmtree(task_dir)
                logger.info(f"Đã xoá thư mục task: {task_dir}")

            # Cập nhật index
            index = self._load_index()
            tasks = index.get("tasks", [])
            tasks = [t for t in tasks if t["task_id"] != task_id]
            index["tasks"] = tasks
            self._save_index(index)

            return True
        except Exception as e:
            logger.error(f"Không thể xoá task {task_id}: {e}")
            return False

