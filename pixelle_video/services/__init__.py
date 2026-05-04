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
Pixelle-Video Services

Các service core cung cấp các tính năng đơn vị.

Services:
- LLMService: Sinh văn bản bằng LLM
- TTSService: Text-to-speech
- MediaService: Sinh media (ảnh & video)
- VideoService: Xử lý video
- FrameProcessor: Bộ điều phối xử lý frame
- PersistenceService: Lưu trữ metadata task và storyboard
- HistoryManager: Logic nghiệp vụ quản lý lịch sử
- ComfyBaseService: Class cơ sở cho các service dựa trên ComfyUI
"""

from pixelle_video.services.comfy_base_service import ComfyBaseService
from pixelle_video.services.llm_service import LLMService
from pixelle_video.services.tts_service import TTSService
from pixelle_video.services.media import MediaService
from pixelle_video.services.video import VideoService
from pixelle_video.services.frame_processor import FrameProcessor
from pixelle_video.services.persistence import PersistenceService
from pixelle_video.services.history_manager import HistoryManager

# Alias để tương thích ngược
ImageService = MediaService

__all__ = [
    "ComfyBaseService",
    "LLMService",
    "TTSService",
    "MediaService",
    "ImageService",  # Tương thích ngược
    "VideoService",
    "FrameProcessor",
    "PersistenceService",
    "HistoryManager",
]

