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
Các model dữ liệu Storyboard cho việc tạo video
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict, Any


@dataclass
class StoryboardConfig:
    """Tham số cấu hình storyboard"""

    # Tham số bắt buộc (phải đứng trước trong dataclass)
    media_width: int                           # Chiều rộng media (ảnh hoặc video, bắt buộc)
    media_height: int                          # Chiều cao media (ảnh hoặc video, bắt buộc)

    # Cô lập task
    task_id: Optional[str] = None              # Task ID để cô lập file (tự sinh nếu None)

    n_storyboard: int = 5                      # Số frame storyboard
    min_narration_words: int = 5               # Số từ tối thiểu của lời thuyết minh
    max_narration_words: int = 20              # Số từ tối đa của lời thuyết minh
    min_image_prompt_words: int = 30           # Số từ tối thiểu của prompt ảnh
    max_image_prompt_words: int = 60           # Số từ tối đa của prompt ảnh

    # Tham số video (chỉ fps, kích thước được xác định bởi template frame)
    video_fps: int = 30                        # Tốc độ khung hình

    # Tham số audio
    tts_inference_mode: str = "local"          # Chế độ inference TTS: "local" hoặc "comfyui"
    voice_id: Optional[str] = None             # ID giọng (local: voice ID của Edge TTS; comfyui: theo workflow)
    tts_workflow: Optional[str] = None         # Tên file workflow TTS (chế độ ComfyUI, None = dùng mặc định)
    tts_speed: Optional[float] = None          # Hệ số tốc độ TTS (0.5-2.0, 1.0 = bình thường)
    ref_audio: Optional[str] = None            # Audio tham chiếu để clone giọng (chỉ chế độ ComfyUI)

    # Workflow media
    media_workflow: Optional[str] = None       # Tên file workflow media (ảnh hoặc video, None = dùng mặc định)

    # Template frame (gồm thông tin kích thước trong đường dẫn)
    frame_template: str = "1080x1920/default.html"  # Đường dẫn template kèm kích thước (vd: "1080x1920/default.html")
    template_params: Optional[Dict[str, Any]] = None  # Tham số template tuỳ chỉnh (vd: {"accent_color": "#ff0000"})


@dataclass
class StoryboardFrame:
    """Một frame trong storyboard"""
    index: int                                 # Chỉ số frame (đếm từ 0)
    narration: str                             # Văn bản thuyết minh
    image_prompt: str                          # Prompt tạo ảnh (có thể None nếu chỉ là text hoặc video)

    # Đường dẫn các tài nguyên đã sinh
    audio_path: Optional[str] = None           # Đường dẫn file audio (thuyết minh)
    media_type: Optional[str] = None           # Loại media: "image" hoặc "video" (None nếu không có media)
    image_path: Optional[str] = None           # Đường dẫn ảnh gốc (cho loại image)
    video_path: Optional[str] = None           # Đường dẫn video gốc (cho loại video, trước khi ghép)
    composed_image_path: Optional[str] = None  # Đường dẫn ảnh đã ghép (kèm phụ đề, cho loại image)
    video_segment_path: Optional[str] = None   # Đường dẫn segment video cuối cùng

    # Metadata
    duration: float = 0.0                      # Thời lượng frame (giây, lấy từ audio hoặc video)
    created_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class ContentMetadata:
    """Metadata nội dung dùng cho hiển thị và sinh thuyết minh"""
    title: str                                 # Tiêu đề nội dung
    author: Optional[str] = None               # Tác giả/người tạo
    subtitle: Optional[str] = None             # Phụ đề
    genre: Optional[str] = None                # Thể loại/danh mục
    summary: Optional[str] = None              # Tóm tắt nội dung
    publication_year: Optional[str] = None     # Năm xuất bản
    cover_url: Optional[str] = None            # URL ảnh bìa/thumbnail


@dataclass
class Storyboard:
    """Storyboard hoàn chỉnh"""
    title: str                                 # Tiêu đề video
    config: StoryboardConfig                   # Cấu hình
    frames: List[StoryboardFrame] = field(default_factory=list)

    # Metadata nội dung (tuỳ chọn)
    content_metadata: Optional[ContentMetadata] = None

    # Output cuối cùng
    final_video_path: Optional[str] = None
    total_duration: float = 0.0

    # Metadata
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

    @property
    def is_completed(self) -> bool:
        """Kiểm tra tất cả frame đã được xử lý chưa"""
        return all(
            frame.video_segment_path is not None
            for frame in self.frames
        )

    @property
    def progress(self) -> float:
        """Trả về tiến độ xử lý (0.0-1.0)"""
        if not self.frames:
            return 0.0
        completed = sum(
            1 for frame in self.frames
            if frame.video_segment_path is not None
        )
        return completed / len(self.frames)


@dataclass
class VideoGenerationResult:
    """Kết quả tạo video"""
    video_path: str                            # Đường dẫn video cuối cùng
    storyboard: Storyboard                     # Storyboard hoàn chỉnh
    duration: float                            # Tổng thời lượng
    file_size: int                             # Kích thước file (byte)
    created_at: datetime = field(default_factory=datetime.now)

