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
Tiện ích Edge TTS - Tạm thời không sử dụng

Đây là implementation edge-tts gốc, giữ lại để có thể dùng sau.
Hiện tại, service TTS chỉ dùng workflow ComfyUI.
"""

import asyncio
import ssl
import random
import certifi
import edge_tts as edge_tts_sdk
from edge_tts.exceptions import NoAudioReceived
from loguru import logger
from aiohttp import WSServerHandshakeError, ClientResponseError


# Dùng bundle certifi để xác minh SSL thay vì tắt nó
_USE_CERTIFI_SSL = True

# Cấu hình retry cho Edge TTS (để xử lý lỗi 401 và NoAudioReceived)
_RETRY_COUNT = 5           # Số lần retry mặc định
_RETRY_BASE_DELAY = 1.0     # Độ trễ retry cơ sở (giây, cho exponential backoff)
_MAX_RETRY_DELAY = 10.0     # Độ trễ retry tối đa (giây)

# Cấu hình rate limiting
_REQUEST_DELAY = 0.5        # Độ trễ tối thiểu trước mỗi request (giây)
_MAX_CONCURRENT_REQUESTS = 3  # Số request đồng thời tối đa

# Semaphore toàn cục cho rate limiting (tạo riêng cho mỗi event loop)
_request_semaphore = None
_semaphore_loop = None


def _get_request_semaphore():
    """Lấy hoặc tạo semaphore request cho event loop hiện tại"""
    global _request_semaphore, _semaphore_loop

    try:
        current_loop = asyncio.get_running_loop()
    except RuntimeError:
        # Không có loop đang chạy
        return asyncio.Semaphore(_MAX_CONCURRENT_REQUESTS)

    # Nếu semaphore chưa tồn tại hoặc thuộc loop khác, tạo mới
    if _request_semaphore is None or _semaphore_loop != current_loop:
        _request_semaphore = asyncio.Semaphore(_MAX_CONCURRENT_REQUESTS)
        _semaphore_loop = current_loop

    return _request_semaphore


async def edge_tts(
    text: str,
    voice: str = "[Chinese] zh-CN Yunjian",
    rate: str = "+0%",
    volume: str = "+0%",
    pitch: str = "+0Hz",
    output_path: str = None,
    retry_count: int = _RETRY_COUNT,
    retry_base_delay: float = _RETRY_BASE_DELAY,
) -> bytes:
    """
    Chuyển văn bản thành giọng nói dùng Microsoft Edge TTS

    Service này miễn phí và không yêu cầu API key.
    Hỗ trợ 400+ giọng nói trên 100+ ngôn ngữ.

    Trả về dữ liệu audio dạng bytes (định dạng MP3).

    Bao gồm cơ chế retry tự động với exponential backoff và jitter
    để xử lý lỗi xác thực 401 và sự cố mạng tạm thời.
    Cũng bao gồm giới hạn request đồng thời và rate limiting.

    Args:
        text: Văn bản cần chuyển thành giọng nói
        voice: ID giọng (vd: [Chinese] zh-CN Yunjian, [English] en-US Jenny)
        rate: Tốc độ đọc (vd: +0%, +50%, -20%)
        volume: Âm lượng (vd: +0%, +50%, -20%)
        pitch: Cao độ (vd: +0Hz, +10Hz, -5Hz)
        output_path: Đường dẫn file output tuỳ chọn để lưu audio
        retry_count: Số lần retry khi thất bại (mặc định: 5)
        retry_base_delay: Độ trễ cơ sở cho exponential backoff (mặc định: 1.0s)

    Returns:
        Dữ liệu audio dạng bytes (định dạng MP3)

    Giọng tiếng Trung phổ biến:
    - [Chinese] zh-CN Yunjian (nam, mặc định)
    - [Chinese] zh-CN Xiaoxiao (nữ)
    - [Chinese] zh-CN Yunxi (nam)
    - [Chinese] zh-CN Xiaoyi (nữ)

    Giọng tiếng Anh phổ biến:
    - [English] en-US Jenny (nữ)
    - [English] en-US Guy (nam)
    - [English] en-GB Sonia (nữ, Anh)

    Ví dụ:
        audio_bytes = await edge_tts(
            text="你好，世界！",
            voice="[Chinese] zh-CN Yunjian",
            rate="+20%"
        )
    """
    logger.debug(f"Đang gọi Edge TTS với voice: {voice}, rate: {rate}, retry_count: {retry_count}")

    # Dùng semaphore để giới hạn request đồng thời
    request_semaphore = _get_request_semaphore()
    async with request_semaphore:
        # Thêm độ trễ ngẫu nhiên nhỏ trước mỗi request để tránh rate limiting
        pre_delay = _REQUEST_DELAY + random.uniform(0, 0.3)
        logger.debug(f"Đang đợi {pre_delay:.2f}s trước request (rate limiting)")
        await asyncio.sleep(pre_delay)

        last_error = None

        # Vòng lặp retry
        for attempt in range(retry_count + 1):  # +1 vì lần thử đầu không phải retry
            if attempt > 0:
                # Exponential backoff kèm jitter
                # delay = base * (2 ^ attempt) + jitter ngẫu nhiên
                exponential_delay = retry_base_delay * (2 ** (attempt - 1))
                jitter = random.uniform(0, retry_base_delay)
                retry_delay = min(exponential_delay + jitter, _MAX_RETRY_DELAY)

                logger.info(f"🔄 Đang thử lại Edge TTS (lần {attempt + 1}/{retry_count + 1}) sau {retry_delay:.2f}s...")
                await asyncio.sleep(retry_delay)

            try:
                # Tạo instance communicate với SSL context certifi
                if _USE_CERTIFI_SSL:
                    if attempt == 0:  # Chỉ log info một lần
                        logger.debug("Đang dùng chứng chỉ SSL certifi cho kết nối Edge TTS an toàn")
                    # Tạo SSL context với bundle certifi
                    import certifi
                    ssl_context = ssl.create_default_context(cafile=certifi.where())
                else:
                    ssl_context = None

                # Tạo instance communicate
                communicate = edge_tts_sdk.Communicate(
                    text=text,
                    voice=voice,
                    rate=rate,
                    volume=volume,
                    pitch=pitch,
                )

                # Thu thập các chunk audio
                audio_chunks = []
                async for chunk in communicate.stream():
                    if chunk["type"] == "audio":
                        audio_chunks.append(chunk["data"])

                audio_data = b"".join(audio_chunks)

                if attempt > 0:
                    logger.success(f"✅ Retry thành công ở lần {attempt + 1}")

                logger.info(f"Đã sinh {len(audio_data)} byte dữ liệu audio")

                # Lưu ra file nếu có output_path
                if output_path:
                    with open(output_path, "wb") as f:
                        f.write(audio_data)
                    logger.info(f"Đã lưu audio tới: {output_path}")

                return audio_data

            except (WSServerHandshakeError, ClientResponseError) as e:
                # Lỗi mạng/xác thực - retry
                last_error = e
                error_code = getattr(e, 'status', 'unknown')
                error_msg = str(e)

                # Log thông tin chi tiết hơn cho lỗi 401
                if error_code == 401 or '401' in error_msg:
                    logger.warning(f"⚠️  Lỗi xác thực Edge TTS 401 (lần {attempt + 1}/{retry_count + 1})")
                    logger.debug(f"Chi tiết lỗi: {error_msg}")
                    logger.debug(f"Thường do rate limiting. Sẽ retry với exponential backoff...")
                else:
                    logger.warning(f"⚠️  Lỗi Edge TTS (lần {attempt + 1}/{retry_count + 1}): {error_code} - {e}")

                if attempt >= retry_count:
                    # Lần thử cuối thất bại
                    logger.error(f"❌ Tất cả {retry_count + 1} lần thử đều thất bại. Lỗi cuối: {error_code}")
                    raise
                # Ngược lại, tiếp tục retry tiếp theo

            except NoAudioReceived as e:
                # NoAudioReceived thường là vấn đề tạm thời - retry với delay dài hơn
                last_error = e
                logger.warning(f"⚠️  Edge TTS NoAudioReceived (lần {attempt + 1}/{retry_count + 1})")
                logger.debug(f"Thường là vấn đề tạm thời của service Microsoft. Sẽ retry với delay dài hơn...")

                if attempt >= retry_count:
                    logger.error(f"❌ Tất cả {retry_count + 1} lần thử thất bại do NoAudioReceived")
                    raise
                # Thêm delay phụ cho lỗi NoAudioReceived
                await asyncio.sleep(2.0)

            except Exception as e:
                # Lỗi khác - không retry, raise ngay
                logger.error(f"Lỗi Edge TTS (không thể retry): {type(e).__name__} - {e}")
                raise

        # Không nên tới đây, nhưng phòng trường hợp
        if last_error:
            raise last_error
        else:
            raise RuntimeError("Edge TTS thất bại mà không có lỗi (bất ngờ)")


def get_audio_duration(audio_path: str) -> float:
    """
    Lấy thời lượng file audio tính bằng giây

    Args:
        audio_path: Đường dẫn file audio

    Returns:
        Thời lượng tính bằng giây
    """
    try:
        # Thử dùng ffmpeg-python
        import ffmpeg
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['format']['duration'])
        return duration
    except Exception as e:
        logger.warning(f"Không thể lấy thời lượng audio: {e}, dùng ước tính")
        # Dự phòng: ước tính dựa trên kích thước file (rất thô)
        import os
        file_size = os.path.getsize(audio_path)
        # Giả định ~16kbps cho MP3, nên 2KB mỗi giây
        estimated_duration = file_size / 2000
        return max(1.0, estimated_duration)  # Tối thiểu 1 giây


async def list_voices(locale: str = None, retry_count: int = _RETRY_COUNT, retry_base_delay: float = _RETRY_BASE_DELAY) -> list[str]:
    """
    Liệt kê tất cả giọng có sẵn cho Edge TTS

    Trả về danh sách ID giọng (ShortName).
    Có thể lọc theo locale.

    Bao gồm cơ chế retry tự động với exponential backoff và jitter
    để xử lý lỗi mạng và rate limiting.

    Args:
        locale: Lọc theo locale (vd: zh-CN, en-US, ja-JP)
        retry_count: Số lần retry khi thất bại (mặc định: 5)
        retry_base_delay: Độ trễ cơ sở cho exponential backoff (mặc định: 1.0s)

    Returns:
        Danh sách ID giọng

    Ví dụ:
        # Liệt kê tất cả giọng
        voices = await list_voices()
        # Trả về: ['[Chinese] zh-CN Yunjian', '[Chinese] zh-CN Xiaoxiao', ...]

        # Chỉ liệt kê giọng tiếng Trung
        voices = await list_voices(locale="zh-CN")
        # Trả về: ['[Chinese] zh-CN Yunjian', '[Chinese] zh-CN Xiaoxiao', ...]
    """
    logger.debug(f"Đang lấy danh sách giọng Edge TTS, lọc locale: {locale}, retry_count: {retry_count}")

    # Dùng semaphore để giới hạn request đồng thời
    request_semaphore = _get_request_semaphore()
    async with request_semaphore:
        # Thêm delay ngẫu nhiên nhỏ trước mỗi request để tránh rate limiting
        pre_delay = _REQUEST_DELAY + random.uniform(0, 0.3)
        logger.debug(f"Đang đợi {pre_delay:.2f}s trước request (rate limiting)")
        await asyncio.sleep(pre_delay)

        last_error = None

        # Vòng lặp retry
        for attempt in range(retry_count + 1):
            if attempt > 0:
                # Exponential backoff kèm jitter
                exponential_delay = retry_base_delay * (2 ** (attempt - 1))
                jitter = random.uniform(0, retry_base_delay)
                retry_delay = min(exponential_delay + jitter, _MAX_RETRY_DELAY)

                logger.info(f"🔄 Đang thử lại list voices (lần {attempt + 1}/{retry_count + 1}) sau {retry_delay:.2f}s...")
                await asyncio.sleep(retry_delay)

            try:
                # Lấy tất cả giọng (edge-tts xử lý SSL nội bộ)
                voices = await edge_tts_sdk.list_voices()

                # Lọc theo locale nếu chỉ định
                if locale:
                    voices = [v for v in voices if v["Locale"].startswith(locale)]

                # Trích xuất ID giọng (ShortName)
                voice_ids = [voice["ShortName"] for voice in voices]

                if attempt > 0:
                    logger.success(f"✅ Retry thành công ở lần {attempt + 1}")

                logger.info(f"Tìm thấy {len(voice_ids)} giọng" + (f" cho locale '{locale}'" if locale else ""))
                return voice_ids

            except (WSServerHandshakeError, ClientResponseError) as e:
                # Lỗi mạng/xác thực - retry
                last_error = e
                error_code = getattr(e, 'status', 'unknown')
                error_msg = str(e)

                # Log thông tin chi tiết hơn cho lỗi 401
                if error_code == 401 or '401' in error_msg:
                    logger.warning(f"⚠️  Lỗi xác thực Edge TTS 401 (list_voices lần {attempt + 1}/{retry_count + 1})")
                    logger.debug(f"Chi tiết lỗi: {error_msg}")
                    logger.debug(f"Thường do rate limiting. Sẽ retry với exponential backoff...")
                else:
                    logger.warning(f"⚠️  Lỗi list voices (lần {attempt + 1}/{retry_count + 1}): {error_code} - {e}")

                if attempt >= retry_count:
                    logger.error(f"❌ Tất cả {retry_count + 1} lần thử thất bại. Lỗi cuối: {error_code}")
                    raise

            except Exception as e:
                # Lỗi khác - không retry, raise ngay
                logger.error(f"Lỗi list voices (không thể retry): {type(e).__name__} - {e}")
                raise

        # Không nên tới đây, nhưng phòng trường hợp
        if last_error:
            raise last_error
        else:
            raise RuntimeError("List voices thất bại mà không có lỗi (bất ngờ)")

