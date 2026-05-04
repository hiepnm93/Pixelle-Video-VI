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
Các endpoint dịch vụ file

Cung cấp truy cập tới các file đã tạo (video, ảnh, audio) và file tài nguyên.
"""

from pathlib import Path
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from loguru import logger

router = APIRouter(prefix="/files", tags=["Files"])


@router.get("/{file_path:path}")
async def get_file(file_path: str):
    """
    Lấy file theo đường dẫn

    Phục vụ file từ các thư mục được phép:
    - output/ - File đã tạo (video, ảnh, audio)
    - workflows/ - File workflow của ComfyUI
    - templates/ - Các template HTML
    - bgm/ - Nhạc nền
    - data/bgm/ - Nhạc nền tuỳ chỉnh
    - data/templates/ - Template tuỳ chỉnh
    - resources/ - Các tài nguyên khác (ảnh, font, v.v.)

    - **file_path**: Đường dẫn file tương đối với các thư mục được phép

    Ví dụ:
    - "abc123.mp4" → output/abc123.mp4
    - "workflows/runninghub/image_flux.json" → workflows/runninghub/image_flux.json
    - "templates/1080x1920/default.html" → templates/1080x1920/default.html
    - "bgm/default.mp3" → bgm/default.mp3
    - "resources/example.png" → resources/example.png

    Trả về file để tải xuống hoặc xem trước.
    """
    try:
        # Định nghĩa các thư mục được phép (theo thứ tự ưu tiên)
        allowed_prefixes = [
            "output/",
            "workflows/",
            "templates/",
            "bgm/",
            "data/bgm/",
            "data/templates/",
            "resources/",
        ]

        # Kiểm tra xem đường dẫn có bắt đầu bằng prefix được phép không, ngược lại thử output/
        full_path = None
        for prefix in allowed_prefixes:
            if file_path.startswith(prefix):
                full_path = file_path
                break

        # Nếu không khớp prefix nào, giả định là trong output/ (tương thích ngược)
        if full_path is None:
            full_path = f"output/{file_path}"

        abs_path = Path.cwd() / full_path

        if not abs_path.exists():
            raise HTTPException(status_code=404, detail=f"Không tìm thấy file: {file_path}")

        if not abs_path.is_file():
            raise HTTPException(status_code=400, detail=f"Đường dẫn không phải là file: {file_path}")

        # Bảo mật: chỉ cho phép truy cập các thư mục đã chỉ định
        try:
            rel_path = abs_path.relative_to(Path.cwd())
            rel_path_str = str(rel_path)

            # Kiểm tra xem đường dẫn có bắt đầu bằng prefix được phép nào không
            is_allowed = any(rel_path_str.startswith(prefix.rstrip('/')) for prefix in allowed_prefixes)

            if not is_allowed:
                raise HTTPException(
                    status_code=403,
                    detail=f"Truy cập bị từ chối: chỉ các thư mục {', '.join(p.rstrip('/') for p in allowed_prefixes)} mới có thể truy cập"
                )
        except ValueError:
            raise HTTPException(status_code=403, detail="Truy cập bị từ chối")

        # Xác định media type
        suffix = abs_path.suffix.lower()
        media_types = {
            '.mp4': 'video/mp4',
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.html': 'text/html',
            '.json': 'application/json',
        }
        media_type = media_types.get(suffix, 'application/octet-stream')

        # Dùng inline disposition để xem trước trên trình duyệt
        return FileResponse(
            path=str(abs_path),
            media_type=media_type,
            headers={
                "Content-Disposition": f'inline; filename="{abs_path.name}"'
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Lỗi truy cập file: {e}")
        raise HTTPException(status_code=500, detail=str(e))
