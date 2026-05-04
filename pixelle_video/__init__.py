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
Pixelle-Video - Trình tạo video bằng AI

Hệ thống dựa trên quy ước với quản lý cấu hình thống nhất.

Cách dùng:
    from pixelle_video import pixelle_video

    # Khởi tạo
    await pixelle_video.initialize()

    # Sử dụng các tính năng
    answer = await pixelle_video.llm("Giải thích về thói quen nguyên tử")
    audio = await pixelle_video.tts("Xin chào thế giới")

    # Tạo video với các pipeline khác nhau
    # Pipeline tiêu chuẩn (mặc định)
    result = await pixelle_video.generate_video(
        text="Cách nâng cao hiệu quả học tập",
        n_scenes=5
    )

    # Pipeline tuỳ chỉnh (mẫu cho logic của riêng bạn)
    result = await pixelle_video.generate_video(
        text=your_content,
        pipeline="custom",
        custom_param_example="custom_value"
    )

    # Kiểm tra các pipeline có sẵn
    print(pixelle_video.pipelines.keys())  # dict_keys(['standard', 'custom'])
"""

from pixelle_video.service import PixelleVideoCore, pixelle_video
from pixelle_video.config import config_manager

__version__ = "0.1.0"

__all__ = ["PixelleVideoCore", "pixelle_video", "config_manager"]

