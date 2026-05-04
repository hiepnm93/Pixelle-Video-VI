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
Service tạo Frame dựa trên HTML

Render các template HTML thành ảnh frame bằng Playwright (headless browser).

Yêu cầu môi trường Linux:
    - Cần cài đặt gói fontconfig
    - Khuyến nghị cài các font cơ bản (ví dụ: fonts-liberation, fonts-noto)

    Ubuntu/Debian: sudo apt-get install -y fontconfig fonts-liberation fonts-noto-cjk
    CentOS/RHEL: sudo yum install -y fontconfig liberation-fonts google-noto-cjk-fonts

    Cài trình duyệt cho Playwright: playwright install --with-deps chromium
"""

import os
import re
import tempfile
import uuid
from typing import Dict, Any, Optional
from pathlib import Path
from loguru import logger

from pixelle_video.utils.template_util import parse_template_size


class HTMLFrameGenerator:
    """
    Bộ tạo frame dựa trên HTML

    Render template HTML thành ảnh frame với cơ chế thay thế biến.
    Sử dụng Playwright để render headless browser một cách ổn định.

    Cách dùng:
        >>> generator = HTMLFrameGenerator("templates/modern.html")
        >>> frame_path = await generator.generate_frame(
        ...     topic="Tại sao đọc sách lại quan trọng",
        ...     text="Đọc sách giúp tạo ra các kết nối thần kinh mới...",
        ...     image="/path/to/image.png",
        ...     ext={"content_title": "Tiêu đề mẫu", "content_author": "Tên tác giả"}
        ... )
    """
    
    _browser = None
    _playwright = None

    def __init__(self, template_path: str):
        """
        Khởi tạo bộ tạo frame HTML

        Args:
            template_path: Đường dẫn tới file template HTML (ví dụ: "templates/1080x1920/default.html")
        """
        self.template_path = template_path
        self.template = self._load_template(template_path)

        # Phân tích kích thước video từ đường dẫn template
        self.width, self.height = parse_template_size(template_path)

        self._check_linux_dependencies()
        logger.debug(f"Đã tải template HTML: {template_path} (kích thước: {self.width}x{self.height})")
    
    
    def _check_linux_dependencies(self):
        """Kiểm tra các phụ thuộc hệ thống Linux và cảnh báo nếu thiếu"""
        if os.name != 'posix':
            return

        try:
            import subprocess

            result = subprocess.run(
                ['fc-list'],
                capture_output=True,
                timeout=2
            )

            if result.returncode != 0:
                logger.warning(
                    "Không tìm thấy fontconfig hoặc fontconfig không hoạt động đúng. "
                    "Cài đặt bằng: sudo apt-get install -y fontconfig fonts-liberation fonts-noto-cjk"
                )
            elif not result.stdout:
                logger.warning(
                    "fontconfig không phát hiện font nào. "
                    "Cài đặt font bằng: sudo apt-get install -y fonts-liberation fonts-noto-cjk"
                )
            else:
                logger.debug(f"Fontconfig đã phát hiện {len(result.stdout.splitlines())} font")

        except FileNotFoundError:
            logger.warning(
                "Không tìm thấy fontconfig (fc-list) trên hệ thống. "
                "Cài đặt bằng: sudo apt-get install -y fontconfig"
            )
        except Exception as e:
            logger.debug(f"Không thể kiểm tra trạng thái fontconfig: {e}")
    
    def _load_template(self, template_path: str) -> str:
        """Tải template HTML từ file"""
        path = Path(template_path)
        if not path.exists():
            raise FileNotFoundError(f"Không tìm thấy template: {template_path}")

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.debug(f"Đã tải template: {len(content)} ký tự")
        return content
    
    def _parse_media_size_from_meta(self) -> tuple[Optional[int], Optional[int]]:
        """
        Phân tích kích thước media từ các thẻ meta trong template

        Tìm các thẻ meta:
        - <meta name="template:media-width" content="1024">
        - <meta name="template:media-height" content="1024">

        Returns:
            Tuple (width, height) hoặc (None, None) nếu không tìm thấy
        """
        from bs4 import BeautifulSoup

        try:
            soup = BeautifulSoup(self.template, 'html.parser')

            width_meta = soup.find('meta', attrs={'name': 'template:media-width'})
            height_meta = soup.find('meta', attrs={'name': 'template:media-height'})

            if width_meta and height_meta:
                width = int(width_meta.get('content', 0))
                height = int(height_meta.get('content', 0))

                if width > 0 and height > 0:
                    logger.debug(f"Đã tìm thấy kích thước media trong thẻ meta: {width}x{height}")
                    return width, height

            return None, None

        except Exception as e:
            logger.warning(f"Không phân tích được kích thước media từ thẻ meta: {e}")
            return None, None
    
    def get_media_size(self) -> tuple[int, int]:
        """
        Lấy kích thước media để tạo image/video

        Trả về kích thước media được khai báo trong các thẻ meta của template.

        Returns:
            Tuple (width, height)
        """
        media_width, media_height = self._parse_media_size_from_meta()

        if media_width and media_height:
            return media_width, media_height

        logger.warning(f"Không tìm thấy thẻ meta kích thước media trong template {self.template_path}, sử dụng giá trị mặc định 1024x1024")
        return 1024, 1024
    
    def parse_template_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Phân tích các tham số tùy chỉnh từ template HTML

        Hỗ trợ cú pháp: {{param:type=default}}
        - {{param}} -> kiểu text, không có default
        - {{param=value}} -> kiểu text, có default
        - {{param:type}} -> kiểu đã chỉ định, không có default
        - {{param:type=value}} -> kiểu đã chỉ định, có default

        Các kiểu được hỗ trợ: text, number, color, bool

        Returns:
            Dictionary các tham số tùy chỉnh kèm cấu hình:
            {
                'param_name': {
                    'type': 'text' | 'number' | 'color' | 'bool',
                    'default': Any,
                    'label': str  # giống với param_name
                }
            }
        """
        PRESET_PARAMS = {'title', 'text', 'image', 'index'}
        
        PARAM_PATTERN = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)(?::([a-z]+))?(?:=([^}]+))?\}\}'
        
        params = {}
        
        for match in re.finditer(PARAM_PATTERN, self.template):
            param_name = match.group(1)
            param_type = match.group(2) or 'text'
            default_value = match.group(3)
            
            if param_name in PRESET_PARAMS:
                continue
            
            if param_name in params:
                continue
            
            if param_type not in {'text', 'number', 'color', 'bool'}:
                logger.warning(f"Kiểu tham số không xác định '{param_type}' cho '{param_name}', đang dùng mặc định 'text'")
                param_type = 'text'
            
            parsed_default = self._parse_default_value(param_type, default_value)
            
            params[param_name] = {
                'type': param_type,
                'default': parsed_default,
                'label': param_name,
            }
        
        if params:
            logger.debug(f"Đã phân tích {len(params)} tham số tùy chỉnh từ template: {list(params.keys())}")

        return params

    def _parse_default_value(self, param_type: str, value_str: Optional[str]) -> Any:
        """
        Phân tích giá trị mặc định dựa trên kiểu tham số

        Args:
            param_type: Kiểu của tham số (text, number, color, bool)
            value_str: Giá trị chuỗi cần phân tích (có thể là None)

        Returns:
            Giá trị đã phân tích với kiểu phù hợp
        """
        if value_str is None:
            return {
                'text': '',
                'number': 0,
                'color': '#000000',
                'bool': False,
            }.get(param_type, '')
        
        if param_type == 'number':
            try:
                if '.' in value_str:
                    return float(value_str)
                else:
                    return int(value_str)
            except ValueError:
                logger.warning(f"Giá trị số không hợp lệ '{value_str}', đang dùng 0")
                return 0
        
        elif param_type == 'bool':
            return value_str.lower() in {'true', '1', 'yes', 'on'}
        
        elif param_type == 'color':
            if value_str.startswith('#'):
                return value_str
            else:
                return f'#{value_str}'
        
        else:  # text
            return value_str
    
    def _replace_parameters(self, html: str, values: Dict[str, Any]) -> str:
        """
        Thay thế các placeholder tham số bằng giá trị thực tế

        Hỗ trợ cú pháp DSL: {{param:type=default}}
        - Nếu giá trị có trong dict values, sử dụng nó
        - Ngược lại, sử dụng giá trị default từ placeholder
        - Nếu không có default, dùng chuỗi rỗng

        Args:
            html: Nội dung template HTML
            values: Dictionary chứa giá trị tham số

        Returns:
            HTML đã thay thế placeholder
        """
        PARAM_PATTERN = r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)(?::([a-z]+))?(?:=([^}]+))?\}\}'
        
        def replacer(match):
            param_name = match.group(1)
            param_type = match.group(2) or 'text'
            default_value_str = match.group(3)
            
            if param_name in values:
                value = values[param_name]
                if isinstance(value, bool):
                    return 'true' if value else 'false'
                return str(value) if value is not None else ''
            
            elif default_value_str:
                return default_value_str
            
            else:
                return ''
        
        return re.sub(PARAM_PATTERN, replacer, html)

    @classmethod
    async def _ensure_browser(cls):
        """Khởi tạo lazy một instance trình duyệt Playwright dùng chung"""
        if cls._browser is None or not cls._browser.is_connected():
            from playwright.async_api import async_playwright
            cls._playwright = await async_playwright().start()
            cls._browser = await cls._playwright.chromium.launch(
                args=[
                    '--no-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-gpu',
                    '--disable-extensions',
                ]
            )
            logger.debug("Đã khởi tạo trình duyệt Playwright Chromium")
        return cls._browser

    @classmethod
    async def close_browser(cls):
        """Tắt instance trình duyệt dùng chung (gọi khi tắt ứng dụng)"""
        if cls._browser:
            await cls._browser.close()
            cls._browser = None
        if cls._playwright:
            await cls._playwright.stop()
            cls._playwright = None
            logger.debug("Đã đóng trình duyệt Playwright")

    async def generate_frame(
        self,
        title: str,
        text: str,
        image: str,
        ext: Optional[Dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> str:
        """
        Tạo frame từ template HTML

        Kích thước video được xác định tự động từ đường dẫn template trong lúc khởi tạo.

        Args:
            title: Tiêu đề video
            text: Nội dung lời thuyết minh cho frame này
            image: Đường dẫn ảnh do AI tạo (hỗ trợ đường dẫn tương đối, tuyệt đối, hoặc HTTP URL)
            ext: Dữ liệu bổ sung (content_title, content_author, v.v.)
            output_path: Đường dẫn output tùy chỉnh (tự động tạo nếu là None)

        Returns:
            Đường dẫn tới ảnh frame được tạo
        """
        if image and not image.startswith(('http://', 'https://', 'data:', 'file://')):
            image_path = Path(image)
            if not image_path.is_absolute():
                image_path = Path.cwd() / image

            if not image_path.exists():
                logger.warning(f"Không tìm thấy file ảnh: {image_path}")
            else:
                image = image_path.as_uri()
                logger.debug(f"Đã chuyển đổi đường dẫn ảnh thành: {image}")
        
        context = {
            "title": title,
            "text": text,
            "image": image,
        }
        
        if ext:
            context.update(ext)
        
        html = self._replace_parameters(self.template, context)

        if output_path is None:
            from pixelle_video.utils.os_util import get_output_path
            output_filename = f"frame_{uuid.uuid4().hex[:16]}.png"
            output_path = get_output_path(output_filename)
        else:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        logger.debug(f"Đang render template HTML ra {output_path} (kích thước: {self.width}x{self.height})")
        tmp_html_path = None
        try:
            browser = await self._ensure_browser()
            page = await browser.new_page(
                viewport={'width': self.width, 'height': self.height},
                device_scale_factor=1,
            )
            try:
                # Ghi HTML ra file tạm và điều hướng qua URL file:// để các tham chiếu
                # ảnh file:// cục bộ được tải trong cùng origin.
                fd, tmp_html_path = tempfile.mkstemp(suffix='.html', prefix='pv_frame_')
                with os.fdopen(fd, 'w', encoding='utf-8') as f:
                    f.write(html)

                await page.goto(Path(tmp_html_path).as_uri(), wait_until='networkidle')
                await page.screenshot(path=output_path, type='png', omit_background=True)
            finally:
                await page.close()
                if tmp_html_path and os.path.exists(tmp_html_path):
                    os.unlink(tmp_html_path)

            logger.info(f"Đã tạo frame: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Không render được template HTML: {e}")
            raise RuntimeError(f"Render HTML thất bại: {e}")
