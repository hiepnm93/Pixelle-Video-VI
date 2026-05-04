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
Các hàm tiện ích sinh nội dung

Các hàm thuần/không trạng thái để sinh nội dung dùng LLM.
Các hàm này có thể tái sử dụng giữa các pipeline khác nhau.
"""

import json
import re
from typing import List, Optional, Literal

from loguru import logger


async def generate_title(
    llm_service,
    content: str,
    strategy: Literal["auto", "direct", "llm"] = "auto",
    max_length: int = 15
) -> str:
    """
    Sinh tiêu đề từ nội dung

    Args:
        llm_service: Instance LLM service
        content: Nội dung nguồn (chủ đề hoặc kịch bản)
        strategy: Chiến lược sinh
            - "auto": Tự quyết định dựa trên độ dài nội dung (mặc định)
            - "direct": Dùng trực tiếp nội dung (cắt nếu cần)
            - "llm": Luôn dùng LLM để sinh tiêu đề
        max_length: Độ dài tiêu đề tối đa (mặc định: 15)

    Returns:
        Tiêu đề đã sinh
    """
    if strategy == "direct":
        content = content.strip()
        return content[:max_length] if len(content) > max_length else content

    if strategy == "auto":
        if len(content.strip()) <= 15:
            return content.strip()
        # Rơi xuống dùng LLM

    # Dùng LLM để sinh tiêu đề
    from pixelle_video.prompts import build_title_generation_prompt

    # Truyền max_length vào prompt để LLM biết giới hạn ký tự
    prompt = build_title_generation_prompt(content, max_length=max_length)
    response = await llm_service(prompt, temperature=0.7, max_tokens=50)

    # Dọn dẹp response
    title = response.strip()

    # Bỏ dấu ngoặc kép nếu có
    if title.startswith('"') and title.endswith('"'):
        title = title[1:-1]
    if title.startswith("'") and title.endswith("'"):
        title = title[1:-1]

    # Bỏ dấu câu cuối
    title = title.rstrip('.,!?;:\'"')

    # An toàn: nếu vẫn vượt giới hạn, cắt thông minh
    if len(title) > max_length:
        # Thử cắt ở ranh giới từ
        truncated = title[:max_length]
        last_space = truncated.rfind(' ')

        # Chỉ dùng ranh giới từ nếu không lùi quá xa (ít nhất 60% của max_length)
        if last_space > max_length * 0.6:
            title = truncated[:last_space]
        else:
            title = truncated

        # Bỏ mọi dấu câu cuối sau khi cắt
        title = title.rstrip('.,!?;:\'"')

    logger.debug(f"Tiêu đề đã sinh: '{title}' (độ dài: {len(title)})")
    return title


async def generate_narrations_from_topic(
    llm_service,
    topic: str,
    n_scenes: int = 5,
    min_words: int = 5,
    max_words: int = 20
) -> List[str]:
    """
    Sinh thuyết minh từ chủ đề bằng LLM

    Args:
        llm_service: Instance LLM service
        topic: Chủ đề/đề tài để sinh thuyết minh
        n_scenes: Số thuyết minh cần sinh
        min_words: Độ dài thuyết minh tối thiểu
        max_words: Độ dài thuyết minh tối đa

    Returns:
        Danh sách văn bản thuyết minh
    """
    from pixelle_video.prompts import build_topic_narration_prompt

    logger.info(f"Đang sinh {n_scenes} thuyết minh từ chủ đề: {topic}")

    prompt = build_topic_narration_prompt(
        topic=topic,
        n_storyboard=n_scenes,
        min_words=min_words,
        max_words=max_words
    )

    response = await llm_service(
        prompt=prompt,
        temperature=0.8,
        max_tokens=2000
    )

    logger.debug(f"Response LLM: {response[:200]}...")

    # Parse JSON
    result = _parse_json(response)

    if "narrations" not in result:
        raise ValueError("Định dạng response không hợp lệ: thiếu key 'narrations'")

    narrations = result["narrations"]

    # Xác thực số lượng
    if len(narrations) > n_scenes:
        logger.warning(f"Nhận được {len(narrations)} thuyết minh, lấy {n_scenes} đầu tiên")
        narrations = narrations[:n_scenes]
    elif len(narrations) < n_scenes:
        raise ValueError(f"Mong đợi {n_scenes} thuyết minh, chỉ nhận được {len(narrations)}")

    logger.info(f"Đã sinh thành công {len(narrations)} thuyết minh")
    return narrations


async def generate_narrations_from_content(
    llm_service,
    content: str,
    n_scenes: int = 5,
    min_words: int = 5,
    max_words: int = 20
) -> List[str]:
    """
    Sinh thuyết minh từ nội dung do người dùng cung cấp bằng LLM

    Args:
        llm_service: Instance LLM service
        content: Nội dung do người dùng cung cấp
        n_scenes: Số thuyết minh cần sinh
        min_words: Độ dài thuyết minh tối thiểu
        max_words: Độ dài thuyết minh tối đa

    Returns:
        Danh sách văn bản thuyết minh
    """
    from pixelle_video.prompts import build_content_narration_prompt

    logger.info(f"Đang sinh {n_scenes} thuyết minh từ nội dung ({len(content)} ký tự)")
    
    prompt = build_content_narration_prompt(
        content=content,
        n_storyboard=n_scenes,
        min_words=min_words,
        max_words=max_words
    )
    
    response = await llm_service(
        prompt=prompt,
        temperature=0.8,
        max_tokens=2000
    )
    
    # Parse JSON
    result = _parse_json(response)

    if "narrations" not in result:
        raise ValueError("Định dạng response không hợp lệ: thiếu key 'narrations'")

    narrations = result["narrations"]

    # Xác thực số lượng
    if len(narrations) > n_scenes:
        logger.warning(f"Nhận được {len(narrations)} thuyết minh, lấy {n_scenes} đầu tiên")
        narrations = narrations[:n_scenes]
    elif len(narrations) < n_scenes:
        raise ValueError(f"Mong đợi {n_scenes} thuyết minh, chỉ nhận được {len(narrations)}")

    logger.info(f"Đã sinh thành công {len(narrations)} thuyết minh")
    return narrations


async def split_narration_script(
    script: str,
    split_mode: Literal["paragraph", "line", "sentence"] = "paragraph",
) -> List[str]:
    """
    Tách kịch bản thuyết minh do người dùng cung cấp thành các đoạn

    Args:
        script: Kịch bản thuyết minh cố định
        split_mode: Chiến lược tách
            - "paragraph": Tách theo dòng trống đôi (\\n\\n), giữ dòng trống đơn trong đoạn
            - "line": Tách theo dòng trống đơn (\\n), mỗi dòng là một đoạn
            - "sentence": Tách theo dấu câu kết thúc (。.!?！？)

    Returns:
        Danh sách các đoạn thuyết minh
    """
    logger.info(f"Đang tách kịch bản (mode={split_mode}, độ dài={len(script)} ký tự)")

    narrations = []

    if split_mode == "paragraph":
        # Tách theo dòng trống đôi (chế độ paragraph)
        # Giữ các dòng trống đơn trong đoạn
        paragraphs = re.split(r'\n\s*\n', script)
        for para in paragraphs:
            # Chỉ strip whitespace đầu/cuối, giữ các dòng trống bên trong
            cleaned = para.strip()
            if cleaned:
                narrations.append(para)
        logger.info(f"✅ Đã tách kịch bản thành {len(narrations)} đoạn (theo paragraph)")

    elif split_mode == "line":
        # Tách theo dòng trống đơn (hành vi gốc)
        narrations = [line.strip() for line in script.split('\n') if line.strip()]
        logger.info(f"✅ Đã tách kịch bản thành {len(narrations)} đoạn (theo line)")

    elif split_mode == "sentence":
        # Tách theo dấu câu kết thúc
        # Hỗ trợ tiếng Trung (。！？) và tiếng Anh (.!?)
        # Dùng regex để tách nhưng giữ câu nguyên vẹn
        cleaned = re.sub(r'\s+', ' ', script.strip())
        # Tách tại dấu câu kết thúc, giữ dấu câu cùng câu
        sentences = re.split(r'(?<=[。.!?！？])\s*', cleaned)
        narrations = [s.strip() for s in sentences if s.strip()]
        logger.info(f"✅ Đã tách kịch bản thành {len(narrations)} đoạn (theo sentence)")

    else:
        # Dự phòng về chế độ line
        logger.warning(f"split_mode '{split_mode}' không xác định, dự phòng về 'line'")
        narrations = [line.strip() for line in script.split('\n') if line.strip()]

    # Log thống kê
    if narrations:
        lengths = [len(s) for s in narrations]
        logger.info(f"   Min: {min(lengths)} ký tự, Max: {max(lengths)} ký tự, Tb: {sum(lengths)//len(lengths)} ký tự")

    return narrations


async def generate_image_prompts(
    llm_service,
    narrations: List[str],
    min_words: int = 30,
    max_words: int = 60,
    batch_size: int = 10,
    max_retries: int = 3,
    progress_callback: Optional[callable] = None
) -> List[str]:
    """
    Sinh prompt ảnh từ thuyết minh (kèm chia batch và retry)

    Args:
        llm_service: Instance LLM service
        narrations: Danh sách thuyết minh
        min_words: Độ dài prompt ảnh tối thiểu
        max_words: Độ dài prompt ảnh tối đa
        batch_size: Số thuyết minh tối đa mỗi batch (mặc định: 10)
        max_retries: Số lần retry tối đa mỗi batch (mặc định: 3)
        progress_callback: Callback tuỳ chọn(completed, total, message) cho cập nhật tiến độ

    Returns:
        Danh sách prompt ảnh (prompt cơ sở, chưa áp dụng tiền tố)
    """
    from pixelle_video.prompts import build_image_prompt_prompt

    logger.info(f"Đang sinh prompt ảnh cho {len(narrations)} thuyết minh (batch_size={batch_size})")

    # Chia thuyết minh thành các batch
    batches = [narrations[i:i + batch_size] for i in range(0, len(narrations), batch_size)]
    logger.info(f"Đã chia thành {len(batches)} batch")

    all_prompts = []

    # Xử lý từng batch
    for batch_idx, batch_narrations in enumerate(batches, 1):
        logger.info(f"Đang xử lý batch {batch_idx}/{len(batches)} ({len(batch_narrations)} thuyết minh)")

        # Logic retry cho batch này
        for attempt in range(1, max_retries + 1):
            try:
                # Sinh prompt cho batch này
                prompt = build_image_prompt_prompt(
                    narrations=batch_narrations,
                    min_words=min_words,
                    max_words=max_words
                )

                response = await llm_service(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=8192
                )

                logger.debug(f"Batch {batch_idx} lần {attempt}: độ dài response LLM: {len(response)} ký tự")

                # Parse JSON
                result = _parse_json(response)

                if "image_prompts" not in result:
                    raise KeyError("Định dạng response không hợp lệ: thiếu 'image_prompts'")

                batch_prompts = result["image_prompts"]

                # Xác thực số lượng
                if len(batch_prompts) != len(batch_narrations):
                    error_msg = (
                        f"Batch {batch_idx} không khớp số lượng prompt (lần {attempt}/{max_retries}):\n"
                        f"  Mong đợi: {len(batch_narrations)} prompt\n"
                        f"  Nhận được: {len(batch_prompts)} prompt"
                    )
                    logger.warning(error_msg)

                    if attempt < max_retries:
                        logger.info(f"Đang thử lại batch {batch_idx}...")
                        continue
                    else:
                        raise ValueError(error_msg)

                # Thành công!
                logger.info(f"✅ Batch {batch_idx} hoàn thành thành công ({len(batch_prompts)} prompt)")
                all_prompts.extend(batch_prompts)

                # Báo cáo tiến độ
                if progress_callback:
                    progress_callback(
                        len(all_prompts),
                        len(narrations),
                        f"Batch {batch_idx}/{len(batches)} hoàn thành"
                    )

                break

            except json.JSONDecodeError as e:
                logger.error(f"Lỗi parse JSON batch {batch_idx} (lần {attempt}/{max_retries}): {e}")
                if attempt >= max_retries:
                    raise
                logger.info(f"Đang thử lại batch {batch_idx}...")

    logger.info(f"✅ Đã sinh {len(all_prompts)} prompt ảnh")
    return all_prompts


async def generate_video_prompts(
    llm_service,
    narrations: List[str],
    min_words: int = 30,
    max_words: int = 60,
    batch_size: int = 10,
    max_retries: int = 3,
    progress_callback: Optional[callable] = None
) -> List[str]:
    """
    Sinh prompt video từ thuyết minh (kèm chia batch và retry)

    Args:
        llm_service: Instance LLM service
        narrations: Danh sách thuyết minh
        min_words: Độ dài prompt video tối thiểu
        max_words: Độ dài prompt video tối đa
        batch_size: Số thuyết minh tối đa mỗi batch (mặc định: 10)
        max_retries: Số lần retry tối đa mỗi batch (mặc định: 3)
        progress_callback: Callback tuỳ chọn(completed, total, message) cho cập nhật tiến độ

    Returns:
        Danh sách prompt video (prompt cơ sở, chưa áp dụng tiền tố)
    """
    from pixelle_video.prompts.video_generation import build_video_prompt_prompt

    logger.info(f"Đang sinh prompt video cho {len(narrations)} thuyết minh (batch_size={batch_size})")

    # Chia thuyết minh thành các batch
    batches = [narrations[i:i + batch_size] for i in range(0, len(narrations), batch_size)]
    logger.info(f"Đã chia thành {len(batches)} batch")

    all_prompts = []

    # Xử lý từng batch
    for batch_idx, batch_narrations in enumerate(batches, 1):
        logger.info(f"Đang xử lý batch {batch_idx}/{len(batches)} ({len(batch_narrations)} thuyết minh)")

        # Logic retry cho batch này
        for attempt in range(1, max_retries + 1):
            try:
                # Sinh prompt cho batch này
                prompt = build_video_prompt_prompt(
                    narrations=batch_narrations,
                    min_words=min_words,
                    max_words=max_words
                )

                response = await llm_service(
                    prompt=prompt,
                    temperature=0.7,
                    max_tokens=8192
                )

                logger.debug(f"Batch {batch_idx} lần {attempt}: độ dài response LLM: {len(response)} ký tự")

                # Parse JSON
                result = _parse_json(response)

                if "video_prompts" not in result:
                    raise KeyError("Định dạng response không hợp lệ: thiếu 'video_prompts'")

                batch_prompts = result["video_prompts"]

                # Xác thực kết quả batch
                if len(batch_prompts) != len(batch_narrations):
                    raise ValueError(
                        f"Không khớp số lượng prompt: mong đợi {len(batch_narrations)}, nhận được {len(batch_prompts)}"
                    )

                # Thành công - thêm vào all_prompts
                all_prompts.extend(batch_prompts)
                logger.info(f"✓ Batch {batch_idx} hoàn thành: {len(batch_prompts)} prompt video")

                # Báo cáo tiến độ
                if progress_callback:
                    completed = len(all_prompts)
                    total = len(narrations)
                    progress_callback(completed, total, f"Batch {batch_idx}/{len(batches)} hoàn thành")

                break  # Thành công, chuyển sang batch tiếp theo

            except Exception as e:
                logger.warning(f"✗ Batch {batch_idx} lần {attempt} thất bại: {e}")
                if attempt >= max_retries:
                    raise
                logger.info(f"Đang thử lại batch {batch_idx}...")

    logger.info(f"✅ Đã sinh {len(all_prompts)} prompt video")
    return all_prompts


def _parse_json(text: str) -> dict:
    """
    Parse JSON từ văn bản, có dự phòng trích xuất JSON từ code block markdown

    Args:
        text: Văn bản chứa JSON

    Returns:
        Dict JSON đã parse

    Raises:
        json.JSONDecodeError: Nếu không tìm thấy JSON hợp lệ
    """
    # Thử parse trực tiếp trước
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Thử trích xuất JSON từ code block markdown
    json_pattern = r'```(?:json)?\s*([\s\S]+?)\s*```'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # Thử tìm bất kỳ object JSON nào trong văn bản
    json_pattern = r'\{[^{}]*(?:"narrations"|"image_prompts")\s*:\s*\[[^\]]*\][^{}]*\}'
    match = re.search(json_pattern, text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except json.JSONDecodeError:
            pass

    # Nếu tất cả thất bại, raise lỗi
    raise json.JSONDecodeError("Không tìm thấy JSON hợp lệ", text, 0)

