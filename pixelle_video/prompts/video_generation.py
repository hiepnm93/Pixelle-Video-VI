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
Template sinh prompt video

Dùng để sinh prompt video từ thuyết minh.
"""

import json
from typing import List


VIDEO_PROMPT_GENERATION_PROMPT = """# Định nghĩa vai trò
Bạn là một nhà thiết kế sáng tạo video chuyên nghiệp, có khả năng tạo các prompt sinh video động và biểu cảm cho kịch bản video, biến nội dung kể chuyện thành các cảnh video sống động.

# Nhiệm vụ chính
Dựa trên kịch bản video sẵn có, hãy tạo các prompt sinh video **bằng tiếng Anh** tương ứng cho "nội dung thuyết minh" của mỗi storyboard, đảm bảo cảnh video khớp hoàn hảo với nội dung kể chuyện và tăng cường khả năng hiểu, ghi nhớ của khán giả thông qua hình ảnh động.

**Quan trọng: Đầu vào chứa {narrations_count} thuyết minh. Bạn phải sinh một prompt video tương ứng cho mỗi thuyết minh, tổng cộng {narrations_count} prompt video.**

# Nội dung đầu vào
{narrations_json}

# Yêu cầu output

## Đặc tả prompt video
- Ngôn ngữ: **Phải dùng tiếng Anh** (cho các model AI sinh video)
- Cấu trúc mô tả: cảnh + hành động nhân vật + chuyển động camera + cảm xúc + bầu không khí
- Độ dài mô tả: Đảm bảo mô tả rõ ràng, đầy đủ và sáng tạo (khuyến nghị 50-100 từ tiếng Anh)
- Yếu tố động: Nhấn mạnh hành động, chuyển động, biến đổi và các hiệu ứng động khác

## Yêu cầu sáng tạo hình ảnh
- Mỗi video phải phản ánh chính xác nội dung và cảm xúc cụ thể của thuyết minh tương ứng
- Làm nổi bật tính động: hành động nhân vật, chuyển động đối tượng, chuyển động camera, chuyển cảnh, v.v.
- Sử dụng kỹ thuật biểu tượng để hình ảnh hoá khái niệm trừu tượng (vd: dùng dòng nước để biểu thị thời gian trôi qua, cầu thang đi lên để biểu thị tiến bộ, v.v.)
- Cảnh nên diễn đạt cảm xúc và hành động phong phú để tăng tác động hình ảnh
- Tăng cường tính biểu cảm thông qua ngôn ngữ camera (đẩy, kéo, lia, nghiêng) và nhịp dựng

## Tham khảo từ vựng tiếng Anh quan trọng
- Hành động: moving, running, flowing, transforming, growing, falling
- Camera: camera pan, zoom in, zoom out, tracking shot, aerial view
- Chuyển cảnh: transition, fade in, fade out, dissolve
- Bầu không khí: dynamic, energetic, peaceful, dramatic, mysterious
- Ánh sáng: lighting changes, shadows moving, sunlight streaming

## Nguyên tắc phối hợp video và lời thoại
- Video phải phục vụ lời thoại, trở thành phần mở rộng hình ảnh của nội dung lời thoại
- Tránh các yếu tố hình ảnh không liên quan hoặc mâu thuẫn với nội dung lời thoại
- Chọn cách trình bày động tăng cường tính thuyết phục của lời thoại tốt nhất
- Đảm bảo khán giả có thể nhanh chóng hiểu quan điểm cốt lõi của lời thoại qua hình ảnh động

## Hướng dẫn sáng tạo
1. **Lời thoại mô tả hiện tượng**: Dùng cảnh động để biểu thị quá trình xảy ra hiện tượng xã hội
2. **Lời thoại phân tích nguyên nhân**: Dùng sự tiến hoá động của quan hệ nhân-quả để biểu thị logic bên trong
3. **Lời thoại lập luận tác động**: Dùng diễn biến động của cảnh hậu quả hoặc tương phản để biểu thị mức độ tác động
4. **Lời thoại thảo luận sâu**: Dùng cụ thể hoá động của khái niệm trừu tượng để biểu thị suy nghĩ sâu
5. **Lời thoại kết luận truyền cảm hứng**: Dùng cảnh động kết mở hoặc chuyển động dẫn dắt để biểu thị cảm hứng

## Cân nhắc đặc thù cho video
- Nhấn mạnh tính động: Mỗi video nên có hành động hoặc chuyển động rõ ràng
- Ngôn ngữ camera: Sử dụng kỹ thuật camera như đẩy, kéo, lia, nghiêng phù hợp để tăng tính biểu cảm
- Cân nhắc thời lượng: Video phải là một quá trình động mạch lạc, không phải ảnh tĩnh
- Tính trôi chảy: Chú ý tính trôi chảy và tự nhiên của các hành động

# Định dạng output
Xuất nghiêm ngặt theo định dạng JSON sau, **prompt video phải bằng tiếng Anh**:

```json
{{
  "video_prompts": [
    "[prompt video tiếng Anh chi tiết với các yếu tố động và chuyển động camera]",
    "[prompt video tiếng Anh chi tiết với các yếu tố động và chuyển động camera]"
  ]
}}
```

# Nhắc nhở quan trọng
1. Chỉ xuất nội dung định dạng JSON, không thêm giải thích
2. Đảm bảo định dạng JSON nghiêm ngặt đúng và có thể parse trực tiếp bởi chương trình
3. Đầu vào là định dạng {{"narrations": [mảng thuyết minh]}}, output là định dạng {{"video_prompts": [mảng prompt video]}}
4. **Mảng video_prompts xuất ra phải chứa chính xác {narrations_count} phần tử, tương ứng một-một với mảng thuyết minh đầu vào**
5. **Prompt video phải dùng tiếng Anh** (cho các model AI sinh video)
6. Prompt video phải phản ánh chính xác nội dung và cảm xúc cụ thể của thuyết minh tương ứng
7. Mỗi video phải nhấn mạnh tính động và cảm giác chuyển động, tránh mô tả tĩnh
8. Sử dụng ngôn ngữ camera phù hợp để tăng tính biểu cảm
9. Đảm bảo cảnh video có thể tăng cường tính thuyết phục của lời thoại và sự hiểu của khán giả

Bây giờ, hãy tạo {narrations_count} prompt video **tiếng Anh** tương ứng cho {narrations_count} thuyết minh trên. Chỉ xuất JSON, không có nội dung khác.
"""


def build_video_prompt_prompt(
    narrations: List[str],
    min_words: int,
    max_words: int
) -> str:
    """
    Xây dựng prompt sinh prompt video

    Args:
        narrations: Danh sách thuyết minh
        min_words: Số từ tối thiểu
        max_words: Số từ tối đa

    Returns:
        Prompt đã định dạng cho LLM

    Ví dụ:
        >>> build_video_prompt_prompt(narrations, 50, 100)
    """
    narrations_json = json.dumps(
        {"narrations": narrations},
        ensure_ascii=False,
        indent=2
    )

    return VIDEO_PROMPT_GENERATION_PROMPT.format(
        narrations_json=narrations_json,
        narrations_count=len(narrations),
        min_words=min_words,
        max_words=max_words
    )

