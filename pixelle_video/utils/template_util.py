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
Các hàm tiện ích Template để parse kích thước và quản lý template
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional, Literal
from pydantic import BaseModel, Field
import logging

from pixelle_video.utils.os_util import (
    get_resource_path,
    list_resource_files,
    list_resource_dirs,
    resource_exists
)

logger = logging.getLogger(__name__)


def parse_template_size(template_path: str) -> Tuple[int, int]:
    """
    Parse kích thước video từ đường dẫn template

    Args:
        template_path: Đường dẫn template như "templates/1080x1920/default.html"
                      hoặc "1080x1920/default.html"

    Returns:
        Tuple (width, height) tính bằng pixel

    Raises:
        ValueError: Nếu định dạng đường dẫn template không hợp lệ

    Ví dụ:
        >>> parse_template_size("templates/1080x1920/default.html")
        (1080, 1920)
        >>> parse_template_size("1920x1080/modern.html")
        (1920, 1080)
    """
    path = Path(template_path)

    # Lấy tên thư mục cha (nên giống như "1080x1920")
    dir_name = path.parent.name

    # Trường hợp đặc biệt: nếu cha là "templates", lên thêm một mức
    if dir_name == "templates":
        # Việc này không nên xảy ra trong cấu trúc mới, nhưng vẫn xử lý
        raise ValueError(
            f"Định dạng đường dẫn template không hợp lệ: {template_path}. "
            f"Định dạng mong đợi: 'WIDTHxHEIGHT/template.html' hoặc 'templates/WIDTHxHEIGHT/template.html'"
        )

    # Parse kích thước từ tên thư mục
    if 'x' not in dir_name:
        raise ValueError(
            f"Định dạng kích thước không hợp lệ trong đường dẫn: {template_path}. "
            f"Tên thư mục phải là 'WIDTHxHEIGHT' (vd: '1080x1920')"
        )

    try:
        width_str, height_str = dir_name.split('x')
        width = int(width_str)
        height = int(height_str)

        # Kiểm tra hợp lý
        if width < 100 or height < 100 or width > 10000 or height > 10000:
            raise ValueError(f"Kích thước không hợp lệ: {width}x{height}")

        return (width, height)
    except ValueError as e:
        raise ValueError(
            f"Không thể parse kích thước từ đường dẫn: {template_path}. "
            f"Định dạng mong đợi: 'WIDTHxHEIGHT/template.html' (vd: '1080x1920/default.html'). "
            f"Lỗi: {e}"
        )


def list_available_sizes() -> List[str]:
    """
    Liệt kê tất cả kích thước video có sẵn (gộp từ templates/ và data/templates/)

    Returns:
        Danh sách chuỗi kích thước như ["1080x1920", "1920x1080", "1080x1080"]

    Ví dụ:
        >>> list_available_sizes()
        ['1080x1920', '1920x1080', '1080x1080']
    """
    # Dùng resource API mới để gộp thư mục mặc định và tuỳ chỉnh
    all_dirs = list_resource_dirs("templates")

    # Chỉ lọc các định dạng kích thước hợp lệ (WIDTHxHEIGHT)
    sizes = []
    for dir_name in all_dirs:
        if 'x' in dir_name:
            try:
                width, height = dir_name.split('x')
                int(width)
                int(height)
                sizes.append(dir_name)
            except (ValueError, AttributeError):
                # Bỏ qua thư mục không hợp lệ
                continue

    return sorted(sizes)


def list_templates_for_size(size: str) -> List[str]:
    """
    Liệt kê tất cả template có sẵn cho một kích thước (gộp từ templates/ và data/templates/)

    Args:
        size: Chuỗi kích thước như "1080x1920"

    Returns:
        Danh sách tên file template (không kèm path) như ["default.html", "modern.html"]

    Ví dụ:
        >>> list_templates_for_size("1080x1920")
        ['cartoon.html', 'default.html', 'elegant.html', 'modern.html', ...]
    """
    # Dùng resource API mới để gộp template mặc định và tuỳ chỉnh
    all_files = list_resource_files("templates", size)

    # Chỉ lọc file HTML
    templates = [f for f in all_files if f.endswith('.html')]

    return sorted(templates)


def get_template_full_path(size: str, template_name: str) -> str:
    """
    Lấy đường dẫn template đầy đủ từ kích thước và tên template (kiểm tra data/templates/ trước, sau đó templates/)

    Args:
        size: Chuỗi kích thước như "1080x1920"
        template_name: Tên file template như "default.html"

    Returns:
        Đường dẫn đầy đủ như "templates/1080x1920/default.html" hoặc "data/templates/1080x1920/default.html"

    Raises:
        FileNotFoundError: Nếu file template không tồn tại ở cả hai vị trí

    Ví dụ:
        >>> get_template_full_path("1080x1920", "default.html")
        'templates/1080x1920/default.html'
    """
    # Dùng resource API mới để tìm tuỳ chỉnh trước, sau đó mặc định
    try:
        return get_resource_path("templates", size, template_name)
    except FileNotFoundError:
        available_templates = list_templates_for_size(size)
        raise FileNotFoundError(
            f"Không tìm thấy template: {size}/{template_name}\n"
            f"Template có sẵn cho kích thước {size}: {available_templates}"
        )


class TemplateDisplayInfo(BaseModel):
    """Thông tin hiển thị template cho lớp UI"""

    name: str = Field(..., description="Tên template không kèm phần mở rộng")
    size: str = Field(..., description="Chuỗi kích thước như '1080x1920'")
    width: int = Field(..., description="Chiều rộng tính bằng pixel")
    height: int = Field(..., description="Chiều cao tính bằng pixel")
    orientation: Literal['portrait', 'landscape', 'square'] = Field(
        ...,
        description="Hướng video"
    )
    is_standard: bool = Field(
        ...,
        description="Chỉ True với các kích thước chuẩn: 1080x1920, 1920x1080, 1080x1080"
    )


class TemplateInfo(BaseModel):
    """Thông tin template hoàn chỉnh kèm đường dẫn và thông tin hiển thị"""

    template_path: str = Field(..., description="Đường dẫn template đầy đủ như '1080x1920/default.html'")
    display_info: TemplateDisplayInfo = Field(..., description="Thông tin hiển thị")


def format_template_display_info(template_name: str, size: str) -> TemplateDisplayInfo:
    """
    Định dạng thông tin hiển thị template cho UI

    Trả về dữ liệu có cấu trúc để lớp UI xử lý hiển thị và i18n.

    Args:
        template_name: Tên file template như "default.html"
        size: Chuỗi kích thước như "1080x1920"

    Returns:
        Object TemplateDisplayInfo kèm tên, kích thước, chiều, hướng và cờ chuẩn

    Ví dụ:
        >>> info = format_template_display_info("default.html", "1080x1920")
        >>> info.name
        'default'
        >>> info.is_standard
        True

        >>> info = format_template_display_info("custom.html", "1080x1921")
        >>> info.orientation
        'portrait'
        >>> info.is_standard
        False
    """
    # Giữ tên template đầy đủ kèm phần mở rộng .html
    name = template_name

    # Parse kích thước
    width, height = map(int, size.split('x'))

    # Phát hiện hướng
    if height > width:
        orientation = 'portrait'
    elif width > height:
        orientation = 'landscape'
    else:
        orientation = 'square'

    # Kiểm tra có phải kích thước chuẩn không (chỉ ba cái này)
    is_standard = (width, height) in [(1080, 1920), (1920, 1080), (1080, 1080)]

    return TemplateDisplayInfo(
        name=name,
        size=size,
        width=width,
        height=height,
        orientation=orientation,
        is_standard=is_standard
    )


def get_all_templates_with_info() -> List[TemplateInfo]:
    """
    Lấy tất cả template kèm thông tin hiển thị

    Returns:
        Danh sách object TemplateInfo

    Ví dụ:
        >>> templates = get_all_templates_with_info()
        >>> for t in templates:
        ...     print(f"{t.display_info.name} - {t.display_info.orientation}")
        ...     print(f"  Đường dẫn: {t.template_path}")
        ...     print(f"  Chuẩn: {t.display_info.is_standard}")
    """
    result = []
    sizes = list_available_sizes()
    
    for size in sizes:
        templates = list_templates_for_size(size)
        for template in templates:
            display_info = format_template_display_info(template, size)
            full_path = f"{size}/{template}"
            result.append(TemplateInfo(
                template_path=full_path,
                display_info=display_info
            ))
    
    return result


def get_templates_grouped_by_size() -> dict:
    """
    Lấy template được nhóm theo kích thước

    Returns:
        Dict với key là kích thước, value là danh sách TemplateInfo
        Sắp xếp theo ưu tiên hướng: portrait > landscape > square

    Ví dụ:
        >>> grouped = get_templates_grouped_by_size()
        >>> for size, templates in grouped.items():
        ...     print(f"Kích thước: {size}")
        ...     for t in templates:
        ...         print(f"  - {t.display_info.name}")
    """
    from collections import defaultdict
    
    templates = get_all_templates_with_info()
    grouped = defaultdict(list)
    
    for t in templates:
        grouped[t.display_info.size].append(t)
    
    # Sort groups by orientation priority: portrait > landscape > square
    orientation_priority = {'portrait': 0, 'landscape': 1, 'square': 2}
    
    sorted_grouped = {}
    for size in sorted(grouped.keys(), key=lambda s: (
        orientation_priority.get(grouped[s][0].display_info.orientation, 3),
        s
    )):
        sorted_grouped[size] = sorted(grouped[size], key=lambda t: t.display_info.name)
    
    return sorted_grouped


def resolve_template_path(template_input: Optional[str]) -> str:
    """
    Phân giải input template thành đường dẫn đầy đủ kèm xác thực (kiểm tra data/templates/ trước, sau đó templates/)

    Args:
        template_input: Có thể là:
            - None: Dùng mặc định "1080x1920/image_default.html"
            - "template.html": Dùng kích thước mặc định + template này
            - "1080x1920/template.html": Đường dẫn tương đối đầy đủ
            - "templates/1080x1920/template.html": Đường dẫn dạng tuyệt đối (cũ)
            - "data/templates/1080x1920/template.html": Đường dẫn tuỳ chỉnh (cũ)

    Returns:
        Đường dẫn đầy đủ đã phân giải (tuỳ chỉnh nếu có, ngược lại là mặc định)

    Raises:
        FileNotFoundError: Nếu template không tồn tại ở cả hai vị trí

    Ví dụ:
        >>> resolve_template_path(None)
        'templates/1080x1920/image_default.html'
        >>> resolve_template_path("image_modern.html")
        'templates/1080x1920/image_modern.html'
        >>> resolve_template_path("1920x1080/image_default.html")
        'templates/1920x1080/image_default.html'
    """
    # Trường hợp mặc định
    if template_input is None:
        template_input = "1080x1920/image_default.html"

    # Parse input để trích xuất kích thước và tên template
    size = None
    template_name = None

    # Xử lý các định dạng input khác nhau
    if template_input.startswith("templates/") or template_input.startswith("data/templates/"):
        # Định dạng đường dẫn đầy đủ cũ - trích xuất kích thước và tên
        parts = Path(template_input).parts
        if len(parts) >= 3:
            size = parts[-2]
            template_name = parts[-1]
    elif '/' in template_input and 'x' in template_input.split('/')[0]:
        # Định dạng "1080x1920/template.html"
        size, template_name = template_input.split('/', 1)
    else:
        # Chỉ tên template - dùng kích thước mặc định
        size = "1080x1920"
        template_name = template_input

    # Tương thích ngược: chuyển "default.html" sang "image_default.html"
    if template_name == "default.html":
        migrated_name = "image_default.html"
        try:
            # Thử tên đã chuyển trước
            path = get_resource_path("templates", size, migrated_name)
            logger.info(f"Tương thích ngược: đã chuyển '{template_input}' thành '{size}/{migrated_name}'")
            return path
        except FileNotFoundError:
            # Rơi xuống thử tên gốc
            logger.warning(f"Không tìm thấy template đã chuyển '{size}/{migrated_name}', đang thử tên gốc")

    # Dùng resource API để phân giải đường dẫn (tuỳ chỉnh > mặc định)
    try:
        return get_resource_path("templates", size, template_name)
    except FileNotFoundError:
        available_sizes = list_available_sizes()
        raise FileNotFoundError(
            f"Không tìm thấy template: {size}/{template_name}\n"
            f"Kích thước có sẵn: {available_sizes}\n"
            f"Gợi ý: Dùng định dạng 'SIZExSIZE/template.html' (vd: '1080x1920/image_default.html')"
        )


def get_template_type(template_name: str) -> Literal['static', 'image', 'video']:
    """
    Phát hiện loại template từ tên file template

    Quy ước đặt tên template:
    - static_*.html: Template phong cách tĩnh (không có media sinh bằng AI)
    - image_*.html: Template yêu cầu ảnh sinh bằng AI
    - video_*.html: Template yêu cầu video sinh bằng AI

    Args:
        template_name: Tên file template như "image_default.html" hoặc "video_simple.html"

    Returns:
        Loại template: 'static', 'image', hoặc 'video'

    Ví dụ:
        >>> get_template_type("static_simple.html")
        'static'
        >>> get_template_type("image_default.html")
        'image'
        >>> get_template_type("video_simple.html")
        'video'
    """
    name = Path(template_name).name

    if name.startswith("static_"):
        return "static"
    elif name.startswith("video_"):
        return "video"
    elif name.startswith("image_"):
        return "image"
    else:
        # Dự phòng: thử phát hiện từ tên cũ
        logger.warning(
            f"Template '{template_name}' không tuân theo quy ước đặt tên (static_/image_/video_). "
            f"Mặc định về loại 'image'."
        )
        return "image"


def filter_templates_by_type(
    templates: List[TemplateInfo],
    template_type: Literal['static', 'image', 'video']
) -> List[TemplateInfo]:
    """
    Lọc template theo loại

    Args:
        templates: Danh sách object TemplateInfo
        template_type: Loại để lọc ('static', 'image', hoặc 'video')

    Returns:
        Danh sách TemplateInfo đã lọc

    Ví dụ:
        >>> all_templates = get_all_templates_with_info()
        >>> image_templates = filter_templates_by_type(all_templates, 'image')
        >>> len(image_templates) > 0
        True
    """
    filtered = []
    for t in templates:
        template_name = t.display_info.name
        if get_template_type(template_name) == template_type:
            filtered.append(t)
    return filtered


def get_templates_grouped_by_size_and_type(
    template_type: Optional[Literal['static', 'image', 'video']] = None
) -> dict:
    """
    Lấy template được nhóm theo kích thước, có thể lọc theo loại

    Args:
        template_type: Bộ lọc loại tuỳ chọn ('static', 'image', hoặc 'video')

    Returns:
        Dict với key là kích thước, value là danh sách TemplateInfo
        Sắp xếp theo ưu tiên hướng: portrait > landscape > square

    Ví dụ:
        >>> # Lấy tất cả template
        >>> all_grouped = get_templates_grouped_by_size_and_type()

        >>> # Chỉ lấy template image
        >>> image_grouped = get_templates_grouped_by_size_and_type('image')
    """
    from collections import defaultdict
    
    templates = get_all_templates_with_info()
    
    # Filter by type if specified
    if template_type is not None:
        templates = filter_templates_by_type(templates, template_type)
    
    grouped = defaultdict(list)
    
    for t in templates:
        grouped[t.display_info.size].append(t)
    
    # Sort groups by orientation priority: portrait > landscape > square
    orientation_priority = {'portrait': 0, 'landscape': 1, 'square': 2}
    
    sorted_grouped = {}
    for size in sorted(grouped.keys(), key=lambda s: (
        orientation_priority.get(grouped[s][0].display_info.orientation, 3),
        s
    )):
        sorted_grouped[size] = sorted(grouped[size], key=lambda t: t.display_info.name)
    
    return sorted_grouped

