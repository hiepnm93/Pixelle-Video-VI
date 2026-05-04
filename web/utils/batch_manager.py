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
Trình quản lý batch nhẹ cho Streamlit (phiên bản đơn giản hoá theo YAGNI)
"""
import time
import traceback
from typing import List, Dict, Any, Optional, Callable
from loguru import logger


class SimpleBatchManager:
    """
    Trình quản lý batch cực kỳ đơn giản theo nguyên tắc YAGNI

    Nguyên tắc thiết kế:
    1. Chỉ hỗ trợ chế độ "AI sinh nội dung"
    2. Cùng cấu hình cho mọi video, chỉ khác chủ đề
    3. Không CSV, không validate phức tạp, chỉ vòng lặp và thực thi
    """

    def __init__(self):
        self.results = []
        self.errors = []
        self.current_index = 0
        self.total_count = 0

    def execute_batch(
        self,
        pixelle_video,
        topics: List[str],
        shared_config: Dict[str, Any],
        overall_progress_callback: Optional[Callable] = None,
        task_progress_callback_factory: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Thực thi sinh hàng loạt với cấu hình dùng chung

        Args:
            pixelle_video: Instance PixelleVideoCore
            topics: Danh sách chủ đề (một chủ đề cho mỗi video)
            shared_config: Cấu hình dùng chung cho mọi video
            overall_progress_callback: Callback tiến trình tổng thể
            task_progress_callback_factory: Hàm factory tạo callback cho mỗi task

        Returns:
            {
                "results": [...],
                "errors": [...],
                "total_count": N,
                "success_count": M,
                "failed_count": K
            }
        """
        self.results = []
        self.errors = []
        self.total_count = len(topics)

        logger.info(f"Bắt đầu sinh hàng loạt: {self.total_count} chủ đề")

        for idx, topic in enumerate(topics, 1):
            self.current_index = idx

            # Báo cáo tiến trình tổng thể
            if overall_progress_callback:
                overall_progress_callback(
                    current=idx,
                    total=self.total_count,
                    topic=topic
                )

            try:
                logger.info(f"Task {idx}/{self.total_count} bắt đầu: {topic}")

                # Trích title_prefix từ shared_config (không phải tham số hợp lệ của generate_video)
                title_prefix = shared_config.get("title_prefix")

                # Xây tham số task (gộp topic với cấu hình chung, ngoại trừ title_prefix)
                task_params = {
                    "text": topic,  # Chủ đề làm input
                    "mode": "generate",  # Cố định chế độ
                }

                # Gộp cấu hình chung, loại trừ title_prefix và các giá trị None
                # Lọc bỏ giá trị None để không can thiệp vào logic tham số trong generate_video
                for key, value in shared_config.items():
                    if key != "title_prefix" and value is not None:
                        task_params[key] = value

                # Sinh title sử dụng title_prefix
                if title_prefix:
                    task_params["title"] = f"{title_prefix} - {topic}"
                else:
                    # Dùng chủ đề làm tiêu đề
                    task_params["title"] = topic

                # Thêm callback tiến trình cho từng task
                if task_progress_callback_factory:
                    task_params["progress_callback"] = task_progress_callback_factory(idx, topic)

                # Thực thi sinh video
                from web.utils.async_helpers import run_async
                result = run_async(pixelle_video.generate_video(**task_params))

                # Trích task_id từ video_path (ví dụ: output/20251118_173821_f96a/final.mp4)
                from pathlib import Path
                task_id = Path(result.video_path).parent.name

                # Ghi nhận thành công
                self.results.append({
                    "index": idx,
                    "topic": topic,
                    "task_id": task_id,
                    "video_path": result.video_path,
                    "status": "success"
                })

                logger.info(f"Task {idx}/{self.total_count} hoàn tất: {result.video_path}")

            except Exception as e:
                # Ghi nhận lỗi nhưng vẫn tiếp tục
                error_msg = str(e)
                error_trace = traceback.format_exc()

                logger.error(f"Task {idx}/{self.total_count} thất bại: {error_msg}")
                logger.debug(f"Traceback lỗi:\n{error_trace}")

                self.errors.append({
                    "index": idx,
                    "topic": topic,
                    "error": error_msg,
                    "traceback": error_trace,
                    "status": "failed"
                })

                # Tiếp tục sang task kế tiếp
                continue

        success_count = len(self.results)
        failed_count = len(self.errors)

        logger.info(
            f"Hoàn tất sinh hàng loạt: "
            f"{success_count}/{self.total_count} thành công, "
            f"{failed_count} thất bại"
        )

        return {
            "results": self.results,
            "errors": self.errors,
            "total_count": self.total_count,
            "success_count": success_count,
            "failed_count": failed_count
        }

