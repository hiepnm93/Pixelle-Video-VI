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
Template sinh prompt cho ảnh

Dùng để sinh prompt ảnh từ thuyết minh.
"""

import json
from typing import List, Optional


# ==================== PRESET PHONG CÁCH ẢNH ====================
# Các phong cách hình ảnh định sẵn cho các trường hợp khác nhau

IMAGE_STYLE_PRESETS = {
    "stick_figure": {
        "name": "Phác thảo người que",
        "description": "stick figure style sketch, black and white lines, pure white background, minimalist hand-drawn feel",
        "use_case": "Cảnh chung, đơn giản và trực quan"
    },

    "minimal": {
        "name": "Trừu tượng tối giản",
        "description": "minimalist abstract art, geometric shapes, clean composition, modern design, soft pastel colors",
        "use_case": "Cảm giác hiện đại, nghệ thuật"
    },

    "concept": {
        "name": "Hình ảnh khái niệm",
        "description": "conceptual visual metaphors, symbolic elements, thought-provoking imagery, artistic interpretation",
        "use_case": "Nội dung sâu sắc, suy tư triết học"
    },
}

# Preset mặc định
DEFAULT_IMAGE_STYLE = "stick_figure"


IMAGE_PROMPT_GENERATION_PROMPT = """# Định nghĩa vai trò
Bạn là một nhà thiết kế sáng tạo hình ảnh chuyên nghiệp, có khả năng tạo các prompt ảnh giàu biểu cảm và mang tính biểu tượng cho kịch bản video, biến các khái niệm trừu tượng thành các cảnh hình ảnh cụ thể.

# Nhiệm vụ chính
Dựa trên kịch bản video sẵn có, hãy tạo prompt ảnh **bằng tiếng Anh** tương ứng cho "nội dung thuyết minh" của mỗi storyboard, đảm bảo cảnh hình ảnh khớp hoàn hảo với nội dung kể chuyện và tăng cường khả năng hiểu, ghi nhớ của khán giả.

**Quan trọng: Đầu vào chứa {narrations_count} thuyết minh. Bạn phải sinh một prompt ảnh tương ứng cho mỗi thuyết minh, tổng cộng {narrations_count} prompt ảnh.**

# Nội dung đầu vào
{narrations_json}

# Yêu cầu output

## Đặc tả prompt ảnh
- Ngôn ngữ: **Phải dùng tiếng Anh** (cho các model AI sinh ảnh)
- Cấu trúc mô tả: cảnh + hành động nhân vật + cảm xúc + yếu tố biểu tượng
- Độ dài mô tả: Đảm bảo mô tả rõ ràng, đầy đủ và sáng tạo (khuyến nghị 50-100 từ tiếng Anh)

## Yêu cầu sáng tạo hình ảnh
- Mỗi ảnh phải phản ánh chính xác nội dung và cảm xúc cụ thể của thuyết minh tương ứng
- Sử dụng kỹ thuật biểu tượng để hình ảnh hoá các khái niệm trừu tượng (ví dụ: dùng con đường để biểu thị lựa chọn cuộc đời, dây xích để biểu thị ràng buộc, v.v.)
- Cảnh nên diễn đạt cảm xúc và hành động phong phú để tăng tác động hình ảnh
- Làm nổi bật chủ đề thông qua bố cục và sắp xếp các phần tử, tránh diễn tả quá đơn thuần

## Tham khảo từ vựng tiếng Anh quan trọng
- Yếu tố biểu tượng: symbolic elements
- Biểu cảm: expression / facial expression
- Hành động: action / gesture / movement
- Cảnh: scene / setting
- Bầu không khí: atmosphere / mood

## Nguyên tắc phối hợp hình ảnh và lời thoại
- Ảnh phải phục vụ lời thoại, trở thành phần mở rộng hình ảnh của nội dung lời thoại
- Tránh các yếu tố hình ảnh không liên quan hoặc mâu thuẫn với nội dung lời thoại
- Chọn cách trình bày hình ảnh tăng cường tính thuyết phục của lời thoại tốt nhất
- Đảm bảo khán giả có thể nhanh chóng hiểu quan điểm cốt lõi của lời thoại qua hình ảnh

## Hướng dẫn sáng tạo
1. **Lời thoại mô tả hiện tượng**: Dùng cảnh trực quan để biểu thị hiện tượng xã hội
2. **Lời thoại phân tích nguyên nhân**: Dùng phép ẩn dụ hình ảnh về quan hệ nhân-quả để biểu thị logic bên trong
3. **Lời thoại lập luận tác động**: Dùng cảnh hậu quả hoặc kỹ thuật tương phản để biểu thị mức độ tác động
4. **Lời thoại thảo luận sâu**: Dùng cụ thể hoá các khái niệm trừu tượng để biểu thị suy nghĩ sâu sắc
5. **Lời thoại kết luận truyền cảm hứng**: Dùng cảnh kết mở hoặc các yếu tố dẫn dắt để biểu thị cảm hứng

# Định dạng output
Xuất nghiêm ngặt theo định dạng JSON sau, **prompt ảnh phải bằng tiếng Anh**:

```json
{{
  "image_prompts": [
    "[prompt ảnh tiếng Anh chi tiết theo yêu cầu phong cách]",
    "[prompt ảnh tiếng Anh chi tiết theo yêu cầu phong cách]"
  ]
}}
```

# Nhắc nhở quan trọng
1. Chỉ xuất nội dung định dạng JSON, không thêm giải thích
2. Đảm bảo định dạng JSON nghiêm ngặt đúng và có thể parse trực tiếp bởi chương trình
3. Đầu vào là định dạng {{"narrations": [mảng thuyết minh]}}, output là định dạng {{"image_prompts": [mảng prompt ảnh]}}
4. **Mảng image_prompts xuất ra phải chứa chính xác {narrations_count} phần tử, tương ứng một-một với mảng thuyết minh đầu vào**
5. **Prompt ảnh phải dùng tiếng Anh** (cho các model AI sinh ảnh)
6. Prompt ảnh phải phản ánh chính xác nội dung và cảm xúc cụ thể của thuyết minh tương ứng
7. Mỗi ảnh phải sáng tạo và có tác động hình ảnh, tránh đơn điệu
8. Đảm bảo cảnh hình ảnh có thể tăng cường tính thuyết phục của lời thoại và sự hiểu biết của khán giả

Bây giờ, hãy tạo {narrations_count} prompt ảnh **tiếng Anh** tương ứng cho {narrations_count} thuyết minh trên. Chỉ xuất JSON, không có nội dung khác.
"""


def build_image_prompt_prompt(
    narrations: List[str],
    min_words: int,
    max_words: int
) -> str:
    """
    Xây dựng prompt sinh prompt ảnh

    Lưu ý: Phong cách/tiền tố sẽ được áp dụng sau qua prompt_prefix trong config.

    Args:
        narrations: Danh sách thuyết minh
        min_words: Số từ tối thiểu
        max_words: Số từ tối đa

    Returns:
        Prompt đã định dạng cho LLM

    Ví dụ:
        >>> build_image_prompt_prompt(narrations, 50, 100)
    """
    narrations_json = json.dumps(
        {"narrations": narrations},
        ensure_ascii=False,
        indent=2
    )

    return IMAGE_PROMPT_GENERATION_PROMPT.format(
        narrations_json=narrations_json,
        narrations_count=len(narrations),
        min_words=min_words,
        max_words=max_words
    )

