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
Prompt sinh kịch bản video dựa trên asset

Dùng để sinh kịch bản video dựa trên các asset do người dùng cung cấp.
"""


ASSET_SCRIPT_GENERATION_PROMPT = """Bạn là một nhà sáng tạo kịch bản video chuyên nghiệp. Dựa trên ý định video và các asset có sẵn của người dùng, hãy tạo một kịch bản video dài {duration} giây. Trước tiên, hãy phát hiện ngôn ngữ đầu vào của người dùng - mặc định là tiếng Việt nếu không có chỉ định khác. Tuân thủ chặt chẽ ngôn ngữ đầu vào, đảm bảo lời thoại nhất quán và tương ứng!

## Yêu cầu
{title_section}- Ý định video: {intent}
- Thời lượng mục tiêu: {duration} giây

## Asset có sẵn (dùng đúng đường dẫn trong output)
{assets_text}

## Hướng dẫn sáng tạo
1. Tuân thủ chặt chẽ ngôn ngữ đầu vào - nếu đầu vào là tiếng Việt, output phải là tiếng Việt, v.v.
2. Xác định số cảnh dựa trên thời lượng mục tiêu (thông thường 5-15 giây mỗi cảnh)
3. Gán một asset từ danh sách asset có sẵn cho mỗi cảnh
4. Mỗi cảnh có thể chứa 1-3 câu thuyết minh
5. Cố gắng sử dụng tất cả asset có sẵn, nhưng có thể dùng lại asset nếu cần
6. Tổng thời lượng tất cả các cảnh phải xấp xỉ {duration} giây
{title_instruction}

## Yêu cầu nhất quán ngôn ngữ (bắt buộc thực thi nghiêm ngặt)
- Ngôn ngữ thuyết minh phải khớp với ngôn ngữ ý định video do người dùng nhập
- Nếu ý định video là tiếng Việt, thuyết minh phải bằng tiếng Việt
- Nếu ý định video là tiếng Anh, thuyết minh phải bằng tiếng Anh
- Trừ khi ý định video chỉ định rõ ngôn ngữ output, tuân thủ ngôn ngữ gốc của ý định

## Yêu cầu output
Cung cấp cho mỗi cảnh:
- scene_number: Số thứ tự cảnh (bắt đầu từ 1)
- asset_path: Đường dẫn chính xác chọn từ danh sách asset có sẵn
- narrations: Mảng chứa 1-3 câu thuyết minh
- duration: Thời lượng ước tính (giây)

Bây giờ hãy bắt đầu sinh kịch bản video:"""


def build_asset_script_prompt(
    intent: str,
    duration: int,
    assets_text: str,
    title: str = ""
) -> str:
    """
    Xây dựng prompt sinh kịch bản dựa trên asset

    Args:
        intent: Ý định/mục đích video
        duration: Thời lượng mục tiêu (giây)
        assets_text: Văn bản đã định dạng của các asset có sẵn kèm mô tả
        title: Tiêu đề video (tuỳ chọn)

    Returns:
        Prompt đã định dạng
    """
    title_section = f"- Tiêu đề video: {title}\n" if title else ""
    title_instruction = f"6. Nội dung thuyết minh phải nhất quán với tiêu đề video: {title}\n" if title else ""

    return ASSET_SCRIPT_GENERATION_PROMPT.format(
        duration=duration,
        title_section=title_section,
        intent=intent,
        assets_text=assets_text,
        title_instruction=title_instruction
    )
