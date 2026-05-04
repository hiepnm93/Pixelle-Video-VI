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
Prompt sinh thuyết minh từ nội dung

Dùng để trích xuất/tinh chỉnh thuyết minh từ nội dung do người dùng cung cấp.
"""


CONTENT_NARRATION_PROMPT = """# Định nghĩa vai trò
Trên toàn cục, bạn phải xuất văn bản theo đúng ngôn ngữ tương ứng với ngôn ngữ của người dùng. Mặc định là tiếng Việt nếu nội dung đầu vào là tiếng Việt.
Bạn là một chuyên gia tinh chỉnh nội dung chuyên nghiệp, có khả năng trích xuất các điểm cốt lõi từ nội dung của người dùng và biến chúng thành kịch bản phù hợp cho video ngắn.

# Nhiệm vụ chính
Người dùng sẽ cung cấp nội dung (có thể dài hoặc ngắn), bạn cần trích xuất thuyết minh cho {n_storyboard} storyboard video (để TTS sinh audio cho video).

# Nội dung do người dùng cung cấp
{content}

# Yêu cầu output

## Đặc tả thuyết minh
- Yêu cầu nhất quán ngôn ngữ: Tuân thủ chặt chẽ ngôn ngữ đầu vào - nếu đầu vào là tiếng Việt, output phải là tiếng Việt, v.v.
- Mục đích: Để TTS sinh audio cho video ngắn
- Giới hạn số từ: Kiểm soát chặt chẽ trong khoảng {min_words}~{max_words} từ (tối thiểu không dưới {min_words} từ)
- Định dạng kết câu: Không dùng dấu câu ở cuối
- Chiến lược tinh chỉnh:
  * Nếu nội dung dài: Trích xuất {n_storyboard} điểm cốt lõi, loại bỏ thông tin dư thừa
  * Nếu nội dung ngắn: Mở rộng phù hợp đồng thời giữ quan điểm cốt lõi, thêm ví dụ hoặc giải thích
  * Nếu nội dung vừa đủ: Tối ưu cách diễn đạt để phù hợp hơn với thuyết minh giọng nói
- Yêu cầu phong cách: Giữ quan điểm cốt lõi của nội dung, nhưng diễn đạt theo cách trò chuyện phù hợp với TTS
- Gợi ý mở đầu: Storyboard đầu tiên có thể dùng câu hỏi hoặc giới thiệu cảnh để thu hút người xem
- Nội dung cốt lõi: Các storyboard giữa mở rộng các điểm cốt lõi của nội dung
- Gợi ý kết thúc: Storyboard cuối cùng đưa ra tóm tắt hoặc cảm hứng
- Cảm xúc và giọng điệu: Nhẹ nhàng, chân thành, tự nhiên, như đang chia sẻ quan điểm với một người bạn
- Cấm: Không dùng URL, emoji, đánh số, không nói sáo rỗng hay sáo ngữ
- Kiểm tra số từ: Sau khi tạo, phải tự xác nhận mỗi đoạn không dưới {min_words} từ

## Yêu cầu mạch lạc giữa các storyboard
- {n_storyboard} storyboard phải mở rộng dựa trên quan điểm cốt lõi của nội dung, tạo thành biểu đạt hoàn chỉnh
- Giữ tính logic mạch lạc và chuyển tiếp tự nhiên
- Mỗi storyboard nên nghe giống như cùng một người đang thuyết minh, với giọng điệu nhất quán
- Đảm bảo nội dung tinh chỉnh trung thành với ý nghĩa gốc, nhưng phù hợp hơn cho video ngắn

# Định dạng output
Xuất nghiêm ngặt theo định dạng JSON sau, không thêm bất kỳ giải thích nào:

```json
{{
  "narrations": [
    "Thuyết minh thứ nhất {min_words}~{max_words} từ",
    "Thuyết minh thứ hai {min_words}~{max_words} từ",
    "Thuyết minh thứ ba {min_words}~{max_words} từ"
  ]
}}
```

# Nhắc nhở quan trọng
1. Chỉ xuất nội dung định dạng JSON, không thêm giải thích
2. Đảm bảo định dạng JSON nghiêm ngặt đúng và có thể parse trực tiếp bởi chương trình
3. Thuyết minh phải được kiểm soát chặt chẽ trong khoảng {min_words}~{max_words} từ
4. Phải xuất chính xác {n_storyboard} thuyết minh storyboard
5. Nội dung phải trung thành với ý nghĩa gốc, nhưng được tối ưu cho biểu đạt thuyết minh giọng nói
6. Định dạng output là object JSON {{"narrations": [mảng thuyết minh]}}

Bây giờ, hãy trích xuất {n_storyboard} thuyết minh storyboard từ nội dung trên. Chỉ xuất JSON, không có nội dung khác.
"""


def build_content_narration_prompt(
    content: str,
    n_storyboard: int,
    min_words: int,
    max_words: int
) -> str:
    """
    Xây dựng prompt tinh chỉnh thuyết minh từ nội dung

    Args:
        content: Nội dung do người dùng cung cấp
        n_storyboard: Số frame storyboard
        min_words: Số từ tối thiểu
        max_words: Số từ tối đa

    Returns:
        Prompt đã định dạng
    """
    return CONTENT_NARRATION_PROMPT.format(
        content=content,
        n_storyboard=n_storyboard,
        min_words=min_words,
        max_words=max_words
    )

