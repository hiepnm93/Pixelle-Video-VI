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
Các endpoint render frame/template
"""

from fastapi import APIRouter, HTTPException
from loguru import logger

from api.dependencies import PixelleVideoDep
from api.schemas.frame import FrameRenderRequest, FrameRenderResponse, TemplateParamsResponse
from pixelle_video.services.frame_html import HTMLFrameGenerator
from pixelle_video.utils.template_util import parse_template_size, resolve_template_path

router = APIRouter(prefix="/frame", tags=["Frame Rendering"])


@router.post("/render", response_model=FrameRenderResponse)
async def render_frame(
    request: FrameRenderRequest,
    pixelle_video: PixelleVideoDep
):
    """
    Render một frame đơn lẻ bằng template HTML

    Tạo ảnh frame bằng cách kết hợp template, tiêu đề, văn bản và ảnh.
    Hữu ích để xem trước template hoặc tạo các frame tuỳ chỉnh.

    - **template**: Khoá template (ví dụ: '1080x1920/default.html')
    - **title**: Văn bản tiêu đề (tuỳ chọn)
    - **text**: Nội dung văn bản của frame
    - **image**: Đường dẫn ảnh (có thể là đường dẫn cục bộ hoặc URL)

    Trả về đường dẫn tới ảnh frame đã tạo.

    Ví dụ:
    ```json
    {
        "template": "1080x1920/modern.html",
        "title": "Welcome",
        "text": "This is a beautiful frame with custom styling",
        "image": "resources/example.png"
    }
    ```
    """
    try:
        logger.info(f"Yêu cầu render frame: template={request.template}")

        # Phân giải đường dẫn template (trả về đường dẫn tuyệt đối với prefix "templates/" hoặc "data/templates/")
        template_path = resolve_template_path(request.template)

        # Phân tích kích thước template
        width, height = parse_template_size(template_path)

        # Tạo trình sinh frame HTML
        generator = HTMLFrameGenerator(template_path)

        # Sinh frame
        frame_path = await generator.generate_frame(
            title=request.title,
            text=request.text,
            image=request.image
        )

        return FrameRenderResponse(
            frame_path=frame_path,
            width=width,
            height=height
        )

    except Exception as e:
        logger.error(f"Lỗi render frame: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/template/params", response_model=TemplateParamsResponse)
async def get_template_params(
    template: str
):
    """
    Lấy tham số tuỳ chỉnh của một template

    Trả về các tham số tuỳ chỉnh được định nghĩa trong file template HTML.
    Các tham số này có thể truyền qua `template_params` trong yêu cầu tạo video.

    Tham số template được định nghĩa theo cú pháp: `{{param_name:type=default}}`

    Các kiểu được hỗ trợ:
    - `text`: Nhập chuỗi
    - `number`: Nhập số
    - `color`: Bộ chọn màu (định dạng hex)
    - `bool`: Hộp kiểm boolean

    Ví dụ cú pháp template:
    ```html
    <div style="color: {{accent_color:color=#ff0000}}">
        {{custom_text:text=Hello World}}
    </div>
    ```

    Args:
        template: Đường dẫn template (ví dụ: '1080x1920/image_default.html')

    Returns:
        Tham số template kèm kiểu, giá trị mặc định và nhãn

    Ví dụ phản hồi:
    ```json
    {
        "template": "1080x1920/image_default.html",
        "media_width": 1080,
        "media_height": 1440,
        "params": {
            "accent_color": {
                "type": "color",
                "default": "#ff0000",
                "label": "accent_color"
            },
            "background": {
                "type": "text",
                "default": "https://example.com/bg.jpg",
                "label": "background"
            }
        }
    }
    ```
    """
    try:
        logger.info(f"Lấy tham số template: {template}")

        # Phân giải đường dẫn template
        template_path = resolve_template_path(template)

        # Tạo generator và phân tích tham số
        generator = HTMLFrameGenerator(template_path)
        params = generator.parse_template_parameters()
        media_width, media_height = generator.get_media_size()

        return TemplateParamsResponse(
            template=template,
            media_width=media_width,
            media_height=media_height,
            params=params
        )

    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Không tìm thấy template: {template}")
    except Exception as e:
        logger.error(f"Lỗi lấy tham số template: {e}")
        raise HTTPException(status_code=500, detail=str(e))
