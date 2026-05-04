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
Prompt sinh tiêu đề

Dùng để sinh tiêu đề video từ nội dung.
"""


TITLE_GENERATION_PROMPT = """Hãy tạo một tiêu đề ngắn gọn, hấp dẫn cho nội dung sau.

Nội dung:
{content}

Yêu cầu:
1. **Nhất quán ngôn ngữ (QUAN TRỌNG)**: Tiêu đề PHẢI cùng ngôn ngữ với nội dung đầu vào
   - Nếu nội dung đầu vào là tiếng Việt, tiêu đề PHẢI bằng tiếng Việt
   - Nếu nội dung đầu vào là tiếng Anh, tiêu đề PHẢI bằng tiếng Anh
   - Tuân thủ chặt chẽ ngôn ngữ của nội dung đầu vào

2. **Giới hạn ký tự (QUAN TRỌNG)**: Tiêu đề KHÔNG ĐƯỢC vượt quá {max_length} ký tự
   - Đếm mọi ký tự kể cả khoảng trắng
   - Tiêu đề phải hoàn chỉnh và có nghĩa trong giới hạn này
   - KHÔNG sinh tiêu đề bị cắt ngắn

3. **Thông điệp cốt lõi (QUAN TRỌNG)**: Tiêu đề PHẢI nắm bắt được Ý CHÍNH của nội dung
   - Xác định chủ đề trung tâm hoặc thông điệp chính
   - Đừng chỉ tập trung vào một khía cạnh nếu nội dung có nhiều điểm quan trọng
   - Đảm bảo tiêu đề thể hiện chính xác nội dung là về cái gì

4. **Không có dấu câu ở cuối**: KHÔNG được có bất kỳ dấu câu nào ở cuối tiêu đề
   - Không có dấu chấm (.), phẩy (,), chấm than (!), chấm hỏi (?), v.v.
   - Tiêu đề phải kết thúc bằng một từ hoặc số, không phải dấu câu

5. **Tính hoàn chỉnh**: Đảm bảo tiêu đề là một cụm từ hoàn chỉnh, có nghĩa
   - Không cắt giữa từ hoặc số
   - Không tạo cụm từ chưa hoàn chỉnh như "Dậy sớm để" hoặc "Cách làm"
   - Dùng từ viết tắt hoặc từ ngắn hơn nếu cần để vừa giới hạn

6. **Ví dụ viết tắt** (dùng khi cần để vừa giới hạn ký tự):
   - Cho tiếng Việt:
     * "10.000 đồng" → "10K"
     * "mỗi tháng" → "hàng tháng" hoặc "tháng"
     * "dậy sớm để khoẻ mạnh" → "Thói quen sớm" hoặc "Sống khoẻ"
   - Cho tiếng Anh:
     * "10,000" → "10K"
     * "per month" → "monthly" hoặc "a month"

7. Tóm tắt chính xác nội dung cốt lõi
8. Hấp dẫn và lôi cuốn, phù hợp làm tiêu đề video
9. Chỉ xuất văn bản tiêu đề, không có dấu ngoặc kép, không có giải thích

Tiêu đề:"""


def build_title_generation_prompt(content: str, max_length: int = 15) -> str:
    """
    Xây dựng prompt sinh tiêu đề

    Args:
        content: Nội dung để sinh tiêu đề
        max_length: Độ dài tối đa của tiêu đề tính bằng ký tự (mặc định: 15)

    Returns:
        Prompt đã định dạng kèm giới hạn ký tự
    """
    # Lấy 500 ký tự đầu tiên để tránh prompt quá dài
    content_preview = content[:500]

    return TITLE_GENERATION_PROMPT.format(
        content=content_preview,
        max_length=max_length
    )

