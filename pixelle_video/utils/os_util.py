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
Tiện ích OS cho quản lý file và đường dẫn

Cung cấp các tiện ích để quản lý đường dẫn và file trong Pixelle-Video.
Lấy cảm hứng từ os_util.py của Pixelle-MCP.
"""

import os
import random
from datetime import datetime
from pathlib import Path
from typing import Optional, Tuple, Literal


def get_pixelle_video_root_path() -> str:
    """
    Lấy đường dẫn root của Pixelle-Video

    Dùng biến môi trường PIXELLE_VIDEO_ROOT để xác định gốc project.
    Đảm bảo phân giải đường dẫn tin cậy ở cả môi trường phát triển và đóng gói.

    Returns:
        Đường dẫn root của project dạng chuỗi
    """
    # Kiểm tra biến môi trường (bắt buộc để hoạt động tin cậy)
    env_root = os.environ.get("PIXELLE_VIDEO_ROOT")
    if env_root and Path(env_root).exists():
        return str(Path(env_root).resolve())

    # Dự phòng về thư mục làm việc hiện tại nếu chưa đặt biến môi trường
    # (cho môi trường phát triển nơi biến env có thể chưa được đặt)
    return str(Path.cwd())


def ensure_pixelle_video_root_path() -> str:
    """
    Đảm bảo đường dẫn root Pixelle-Video tồn tại và trả về đường dẫn

    Returns:
        Đường dẫn root dạng chuỗi
    """
    root_path = get_pixelle_video_root_path()
    root_path_obj = Path(root_path)
    output_dir = root_path_obj / 'output'
    output_dir.mkdir(parents=True, exist_ok=True)

    return root_path


def get_root_path(*paths: str) -> str:
    """
    Lấy đường dẫn tương đối so với root của Pixelle-Video

    Args:
        *paths: Các thành phần đường dẫn để ghép

    Returns:
        Đường dẫn tuyệt đối dạng chuỗi

    Ví dụ:
        get_root_path("temp", "audio.mp3")
        # Trả về: "/path/to/project/temp/audio.mp3"
    """
    root_path = ensure_pixelle_video_root_path()
    if paths:
        return os.path.join(root_path, *paths)
    return root_path


def get_temp_path(*paths: str) -> str:
    """
    Lấy đường dẫn tương đối so với thư mục temp của Pixelle-Video

    Đảm bảo thư mục temp tồn tại trước khi trả về đường dẫn.

    Args:
        *paths: Các thành phần đường dẫn để ghép

    Returns:
        Đường dẫn tuyệt đối tới thư mục temp hoặc file

    Ví dụ:
        get_temp_path("audio.mp3")
        # Trả về: "/path/to/project/temp/audio.mp3"
    """
    temp_path = get_root_path("temp")

    # Đảm bảo thư mục temp tồn tại
    os.makedirs(temp_path, exist_ok=True)

    if paths:
        return os.path.join(temp_path, *paths)
    return temp_path


def get_data_path(*paths: str) -> str:
    """
    Lấy đường dẫn tương đối so với thư mục data của Pixelle-Video

    Đảm bảo thư mục data tồn tại trước khi trả về đường dẫn.

    Args:
        *paths: Các thành phần đường dẫn để ghép

    Returns:
        Đường dẫn tuyệt đối tới thư mục data hoặc file

    Ví dụ:
        get_data_path("videos", "output.mp4")
        # Trả về: "/path/to/project/data/videos/output.mp4"
    """
    data_path = get_root_path("data")

    # Đảm bảo thư mục data tồn tại
    os.makedirs(data_path, exist_ok=True)

    if paths:
        return os.path.join(data_path, *paths)
    return data_path


def get_output_path(*paths: str) -> str:
    """
    Lấy đường dẫn tương đối so với thư mục output của Pixelle-Video

    Đảm bảo thư mục output tồn tại trước khi trả về đường dẫn.

    Args:
        *paths: Các thành phần đường dẫn để ghép

    Returns:
        Đường dẫn tuyệt đối tới thư mục output hoặc file

    Ví dụ:
        get_output_path("video.mp4")
        # Trả về: "/path/to/project/output/video.mp4"
    """
    output_path = get_root_path("output")

    # Đảm bảo thư mục output tồn tại
    os.makedirs(output_path, exist_ok=True)

    if paths:
        return os.path.join(output_path, *paths)
    return output_path


def save_bytes_to_file(data: bytes, file_path: str) -> str:
    """
    Lưu dữ liệu bytes ra file

    Tạo các thư mục cha nếu chúng chưa tồn tại.

    Args:
        data: Dữ liệu nhị phân cần lưu
        file_path: Đường dẫn file đích

    Returns:
        Đường dẫn tuyệt đối của file đã lưu

    Ví dụ:
        save_bytes_to_file(audio_data, get_temp_path("audio.mp3"))
    """
    # Đảm bảo thư mục cha tồn tại
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Ghi dữ liệu nhị phân
    with open(file_path, "wb") as f:
        f.write(data)

    return os.path.abspath(file_path)


def ensure_dir(path: str) -> str:
    """
    Đảm bảo thư mục tồn tại, tạo nếu chưa có

    Args:
        path: Đường dẫn thư mục

    Returns:
        Đường dẫn tuyệt đối của thư mục
    """
    os.makedirs(path, exist_ok=True)
    return os.path.abspath(path)


# ========== Quản lý thư mục Task ==========

def create_task_id() -> str:
    """
    Tạo task ID duy nhất với timestamp + hậu tố ngẫu nhiên

    Định dạng: {timestamp}_{random_hex}
    Ví dụ: "20251028_143052_ab3d"

    Xác suất xung đột: < 0.0001% (65536 tổ hợp mỗi giây)

    Returns:
        Chuỗi Task ID
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    random_suffix = f"{random.randint(0, 0xFFFF):04x}"  # hex 4 chữ số (0000-ffff)
    return f"{timestamp}_{random_suffix}"


def create_task_output_dir(task_id: Optional[str] = None) -> Tuple[str, str]:
    """
    Tạo thư mục output cô lập cho một tác vụ tạo video

    Cấu trúc thư mục:
        output/{task_id}/
        ├── final.mp4           # Output video cuối cùng
        ├── frames/             # Tất cả file liên quan tới frame
        │   ├── 01_audio.mp3
        │   ├── 01_image.png
        │   ├── 01_composed.png
        │   ├── 01_segment.mp4
        │   └── ...
        └── metadata.json       # Tuỳ chọn: metadata task

    Args:
        task_id: Task ID tuỳ chọn (tự sinh nếu None)

    Returns:
        Tuple (task_dir, task_id)

    Ví dụ:
        >>> task_dir, task_id = create_task_output_dir()
        >>> # task_dir = "/path/to/project/output/20251028_143052_ab3d"
        >>> # task_id = "20251028_143052_ab3d"
    """
    if task_id is None:
        task_id = create_task_id()

    task_dir = get_output_path(task_id)
    frames_dir = os.path.join(task_dir, "frames")

    # Tạo các thư mục
    os.makedirs(frames_dir, exist_ok=True)

    return task_dir, task_id


def get_task_path(task_id: str, *paths: str) -> str:
    """
    Lấy đường dẫn trong thư mục task

    Args:
        task_id: Task ID
        *paths: Các thành phần đường dẫn để ghép

    Returns:
        Đường dẫn tuyệt đối trong thư mục task

    Ví dụ:
        >>> get_task_path("20251028_143052_ab3d", "final.mp4")
        >>> # Trả về: "/path/to/project/output/20251028_143052_ab3d/final.mp4"
    """
    task_dir = get_output_path(task_id)
    if paths:
        return os.path.join(task_dir, *paths)
    return task_dir


def get_task_frame_path(
    task_id: str,
    frame_index: int,
    file_type: Literal["audio", "image", "video", "composed", "segment"]
) -> str:
    """
    Lấy đường dẫn file frame trong thư mục task

    Args:
        task_id: Task ID
        frame_index: Chỉ số frame (đếm từ 0 nội bộ, nhưng tên file bắt đầu từ 01)
        file_type: Loại file (audio/image/video/composed/segment)

    Returns:
        Đường dẫn tuyệt đối tới file frame

    Ví dụ:
        >>> get_task_frame_path("20251028_143052_ab3d", 0, "audio")
        >>> # Trả về: ".../output/20251028_143052_ab3d/frames/01_audio.mp3"
    """
    ext_map = {
        "audio": "mp3",
        "image": "png",
        "video": "mp4",
        "composed": "png",
        "segment": "mp4"
    }
    
    # Số frame bắt đầu từ 01 để dễ đọc với người
    filename = f"{frame_index + 1:02d}_{file_type}.{ext_map[file_type]}"
    return get_task_path(task_id, "frames", filename)


def get_task_final_video_path(task_id: str) -> str:
    """
    Lấy đường dẫn video cuối cùng trong thư mục task

    Args:
        task_id: Task ID

    Returns:
        Đường dẫn tuyệt đối tới video cuối cùng

    Ví dụ:
        >>> get_task_final_video_path("20251028_143052_ab3d")
        >>> # Trả về: ".../output/20251028_143052_ab3d/final.mp4"
    """
    return get_task_path(task_id, "final.mp4")


# ========== Quản lý Resource (Templates/BGM/Workflows) ==========

def get_resource_path(resource_type: Literal["bgm", "templates", "workflows"], *paths: str) -> str:
    """
    Lấy đường dẫn file resource kèm hỗ trợ ghi đè tuỳ chỉnh

    Thứ tự ưu tiên tìm kiếm:
        1. data/{resource_type}/*paths  (tuỳ chỉnh, ưu tiên cao hơn)
        2. {resource_type}/*paths       (mặc định, dự phòng)

    Args:
        resource_type: Loại resource ("bgm", "templates", "workflows")
        *paths: Các thành phần đường dẫn tương đối so với thư mục resource

    Returns:
        Đường dẫn tuyệt đối tới file resource (tuỳ chỉnh nếu có, ngược lại là mặc định)

    Raises:
        FileNotFoundError: Nếu không tìm thấy file ở cả hai vị trí

    Ví dụ:
        >>> get_resource_path("bgm", "happy.mp3")
        # Trả về: "data/bgm/happy.mp3" (nếu có) hoặc "bgm/happy.mp3"

        >>> get_resource_path("templates", "1080x1920", "default.html")
        # Trả về: "data/templates/1080x1920/default.html" hoặc "templates/1080x1920/default.html"

        >>> get_resource_path("workflows", "selfhost", "image_flux.json")
        # Trả về: "data/workflows/selfhost/image_flux.json" hoặc "workflows/selfhost/image_flux.json"
    """
    # Xây dựng đường dẫn tuỳ chỉnh (data/*)
    custom_path = get_data_path(resource_type, *paths)

    # Xây dựng đường dẫn mặc định (root/*)
    default_path = get_root_path(resource_type, *paths)

    # Ưu tiên: tuỳ chỉnh > mặc định
    if os.path.exists(custom_path):
        return custom_path

    if os.path.exists(default_path):
        return default_path

    # Không tìm thấy ở cả hai vị trí
    raise FileNotFoundError(
        f"Không tìm thấy resource: {os.path.join(resource_type, *paths)}\n"
        f"  Đã tìm tại các vị trí:\n"
        f"    1. {custom_path} (tuỳ chỉnh)\n"
        f"    2. {default_path} (mặc định)"
    )


def list_resource_files(
    resource_type: Literal["bgm", "templates", "workflows"],
    subdir: str = ""
) -> list[str]:
    """
    Liệt kê file resource kèm hỗ trợ ghi đè tuỳ chỉnh

    Gộp file từ cả hai vị trí mặc định và tuỳ chỉnh:
        - File từ data/{resource_type}/* (tuỳ chỉnh, ưu tiên cao hơn)
        - File từ {resource_type}/* (mặc định)
        - Tên trùng được loại bỏ trùng lặp (tuỳ chỉnh được ưu tiên)

    Args:
        resource_type: Loại resource ("bgm", "templates", "workflows")
        subdir: Thư mục con tuỳ chọn (vd: "1080x1920" cho templates)

    Returns:
        Danh sách tên file đã sắp xếp (đã loại trùng, tuỳ chỉnh ghi đè mặc định)

    Ví dụ:
        >>> list_resource_files("bgm")
        # Trả về: ["custom.mp3", "default.mp3", "happy.mp3"]
        # (gộp từ bgm/ và data/bgm/)

        >>> list_resource_files("templates", "1080x1920")
        # Trả về: ["custom.html", "default.html", "modern.html"]
        # (gộp từ templates/1080x1920/ và data/templates/1080x1920/)
    """
    files = {}  # Dùng dict để theo dõi ưu tiên nguồn: {filename: path}

    # Xây dựng đường dẫn thư mục
    default_dir = Path(get_root_path(resource_type, subdir)) if subdir else Path(get_root_path(resource_type))
    custom_dir = Path(get_data_path(resource_type, subdir)) if subdir else Path(get_data_path(resource_type))

    # Quét thư mục mặc định trước (ưu tiên thấp hơn)
    if default_dir.exists() and default_dir.is_dir():
        for item in default_dir.iterdir():
            if item.is_file():
                files[item.name] = str(item)

    # Quét thư mục tuỳ chỉnh (ưu tiên cao hơn, ghi đè)
    if custom_dir.exists() and custom_dir.is_dir():
        for item in custom_dir.iterdir():
            if item.is_file():
                files[item.name] = str(item)  # Ghi đè nếu tồn tại

    return sorted(files.keys())


def list_resource_dirs(
    resource_type: Literal["bgm", "templates", "workflows"]
) -> list[str]:
    """
    Liệt kê các thư mục con trong thư mục resource

    Gộp thư mục từ cả hai vị trí mặc định và tuỳ chỉnh.

    Args:
        resource_type: Loại resource ("bgm", "templates", "workflows")

    Returns:
        Danh sách tên thư mục đã sắp xếp (đã loại trùng)

    Ví dụ:
        >>> list_resource_dirs("templates")
        # Trả về: ["1080x1080", "1080x1920", "1920x1080"]

        >>> list_resource_dirs("workflows")
        # Trả về: ["runninghub", "selfhost"]
    """
    dirs = set()

    # Xây dựng đường dẫn thư mục
    default_dir = Path(get_root_path(resource_type))
    custom_dir = Path(get_data_path(resource_type))

    # Quét thư mục mặc định
    if default_dir.exists() and default_dir.is_dir():
        for item in default_dir.iterdir():
            if item.is_dir():
                dirs.add(item.name)

    # Quét thư mục tuỳ chỉnh
    if custom_dir.exists() and custom_dir.is_dir():
        for item in custom_dir.iterdir():
            if item.is_dir():
                dirs.add(item.name)

    return sorted(dirs)


def resource_exists(resource_type: Literal["bgm", "templates", "workflows"], *paths: str) -> bool:
    """
    Kiểm tra file resource có tồn tại không (ở vị trí tuỳ chỉnh hoặc mặc định)

    Args:
        resource_type: Loại resource ("bgm", "templates", "workflows")
        *paths: Các thành phần đường dẫn tương đối so với thư mục resource

    Returns:
        True nếu tồn tại ở một trong hai vị trí, False nếu không

    Ví dụ:
        >>> resource_exists("bgm", "happy.mp3")
        True

        >>> resource_exists("templates", "1080x1920", "default.html")
        True
    """
    custom_path = get_data_path(resource_type, *paths)
    default_path = get_root_path(resource_type, *paths)

    return os.path.exists(custom_path) or os.path.exists(default_path)

