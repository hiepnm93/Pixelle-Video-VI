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
Service xử lý Video

Service ghép video hiệu năng cao dựa trên ffmpeg-python.

Tính năng:
- Ghép video
- Ghép audio/video
- Thêm nhạc nền
- Chuyển ảnh thành video

Lưu ý: Yêu cầu cài đặt FFmpeg trên hệ thống.
"""

import os
import shutil
import tempfile
import uuid
from pathlib import Path
from typing import List, Literal, Optional

import ffmpeg
from loguru import logger

from pixelle_video.utils.os_util import (
    get_resource_path,
    list_resource_files,
    resource_exists
)


def check_ffmpeg() -> None:
    """
    Kiểm tra FFmpeg đã được cài đặt trên hệ thống chưa

    Raises:
        RuntimeError: Nếu không tìm thấy FFmpeg
    """
    if not shutil.which("ffmpeg"):
        raise RuntimeError(
            "Không tìm thấy FFmpeg. Vui lòng cài đặt:\n"
            "  macOS: brew install ffmpeg\n"
            "  Ubuntu/Debian: apt-get install ffmpeg\n"
            "  Windows: https://ffmpeg.org/download.html"
        )


# Kiểm tra FFmpeg có sẵn khi import module
check_ffmpeg()


class VideoService:
    """
    Bộ ghép video cho các tác vụ xử lý video thông dụng

    Dùng ffmpeg-python cho xử lý video hiệu năng cao.
    Mọi thao tác giữ nguyên chất lượng video khi có thể (stream copy).

    Ví dụ:
        >>> compositor = VideoCompositor()
        >>>
        >>> # Ghép video
        >>> compositor.concat_videos(
        ...     ["intro.mp4", "main.mp4", "outro.mp4"],
        ...     "final.mp4"
        ... )
        >>>
        >>> # Thêm voiceover
        >>> compositor.merge_audio_video(
        ...     "visual.mp4",
        ...     "voiceover.mp3",
        ...     "final.mp4"
        ... )
        >>>
        >>> # Thêm nhạc nền
        >>> compositor.add_bgm(
        ...     "video.mp4",
        ...     "music.mp3",
        ...     "final.mp4",
        ...     bgm_volume=0.3
        ... )
        >>>
        >>> # Tạo video từ ảnh + audio
        >>> compositor.create_video_from_image(
        ...     "frame.png",
        ...     "narration.mp3",
        ...     "segment.mp4"
        ... )
    """
    
    def concat_videos(
        self,
        videos: List[str],
        output: str,
        method: Literal["demuxer", "filter"] = "demuxer",
        bgm_path: Optional[str] = None,
        bgm_volume: float = 0.2,
        bgm_mode: Literal["once", "loop"] = "loop"
    ) -> str:
        """
        Ghép nhiều video thành một

        Args:
            videos: Danh sách đường dẫn file video cần ghép
            output: Đường dẫn file video output
            method: Phương pháp ghép
                - "demuxer": Nhanh, không re-encode (yêu cầu định dạng giống nhau)
                - "filter": Chậm hơn nhưng xử lý được nhiều định dạng khác nhau
            bgm_path: Đường dẫn file nhạc nền (tuỳ chọn)
                - None: Không có BGM
                - Tên file (vd: "default.mp3", "happy.mp3"): Dùng BGM có sẵn trong thư mục bgm/
                - Đường dẫn tuỳ chỉnh: Dùng file BGM tuỳ chỉnh
            bgm_volume: Mức âm lượng BGM (0.0-1.0), mặc định 0.2
            bgm_mode: Chế độ phát BGM
                - "once": Phát BGM một lần
                - "loop": Lặp BGM cho khớp thời lượng video

        Returns:
            Đường dẫn file video output

        Raises:
            ValueError: Nếu danh sách video rỗng
            RuntimeError: Nếu thực thi FFmpeg thất bại

        Lưu ý:
            - Phương pháp demuxer yêu cầu tất cả video phải giống nhau:
              độ phân giải, codec, fps, v.v.
            - Phương pháp filter sẽ re-encode video, chậm hơn nhưng tương thích hơn
        """
        if not videos:
            raise ValueError("Danh sách video không được rỗng")

        if len(videos) == 1:
            logger.info(f"Chỉ có một video, đang copy tới {output}")
            shutil.copy(videos[0], output)
            return output

        logger.info(f"Đang ghép {len(videos)} video bằng phương pháp {method}")

        # Bước 1: Ghép video
        if bgm_path:
            # Nếu cần BGM, ghép vào file tạm trước
            temp_output = output.replace('.mp4', '_no_bgm.mp4')
            concat_result = self._concat_demuxer(videos, temp_output) if method == "demuxer" else self._concat_filter(videos, temp_output)

            # Bước 2: Thêm BGM
            logger.info(f"Đang thêm BGM: {bgm_path} (âm lượng={bgm_volume}, chế độ={bgm_mode})")
            final_result = self._add_bgm_to_video(
                video=concat_result,
                bgm_path=bgm_path,
                output=output,
                volume=bgm_volume,
                mode=bgm_mode
            )

            # Dọn dẹp file tạm
            if os.path.exists(temp_output):
                os.unlink(temp_output)

            return final_result
        else:
            # Không có BGM, ghép trực tiếp
            if method == "demuxer":
                return self._concat_demuxer(videos, output)
            else:
                return self._concat_filter(videos, output)
    
    def _concat_demuxer(self, videos: List[str], output: str) -> str:
        """
        Ghép bằng concat demuxer (nhanh, không re-encode)

        Tương đương FFmpeg:
            ffmpeg -f concat -safe 0 -i filelist.txt -c copy output.mp4
        """
        # Create temporary file list
        with tempfile.NamedTemporaryFile(
            mode='w',
            delete=False,
            suffix='.txt',
            encoding='utf-8'
        ) as f:
            for video in videos:
                abs_path = Path(video).absolute()
                escaped_path = str(abs_path).replace("'", "'\\''")
                f.write(f"file '{escaped_path}'\n")
            filelist = f.name
        
        try:
            logger.debug(f"Đã tạo filelist: {filelist}")
            (
                ffmpeg
                .input(filelist, format='concat', safe=0)
                .output(output, c='copy')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )
            logger.success(f"Đã ghép video thành công: {output}")
            return output
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Lỗi FFmpeg concat: {error_msg}")
            raise RuntimeError(f"Không thể ghép video: {error_msg}")
        finally:
            if os.path.exists(filelist):
                os.unlink(filelist)

    def _concat_filter(self, videos: List[str], output: str) -> str:
        """
        Ghép bằng concat filter (chậm hơn nhưng xử lý được nhiều định dạng)

        Tương đương FFmpeg:
            ffmpeg -i v1.mp4 -i v2.mp4 -filter_complex "[0:v][0:a][1:v][1:a]concat=n=2:v=1:a=1[v][a]"
                   -map "[v]" -map "[a]" output.mp4
        """
        try:
            # Build filter_complex string manually
            n = len(videos)
            
            # Build input stream labels: [0:v][0:a][1:v][1:a]...
            stream_spec = "".join([f"[{i}:v][{i}:a]" for i in range(n)])
            filter_complex = f"{stream_spec}concat=n={n}:v=1:a=1[v][a]"
            
            # Build ffmpeg command
            cmd = ['ffmpeg']
            for video in videos:
                cmd.extend(['-i', video])
            cmd.extend([
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-map', '[a]',
                '-y',  # Ghi đè output
                output
            ])

            # Chạy lệnh
            import subprocess
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=True
            )

            logger.success(f"Đã ghép video thành công: {output}")
            return output
        except subprocess.CalledProcessError as e:
            error_msg = e.stderr if e.stderr else str(e)
            logger.error(f"Lỗi FFmpeg concat filter: {error_msg}")
            raise RuntimeError(f"Không thể ghép video: {error_msg}")
        except Exception as e:
            logger.error(f"Lỗi ghép: {e}")
            raise RuntimeError(f"Không thể ghép video: {e}")

    def _get_video_duration(self, video: str) -> float:
        """Lấy thời lượng video tính bằng giây"""
        try:
            probe = ffmpeg.probe(video)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.warning(f"Không thể lấy thời lượng video: {e}")
            return 0.0

    def _get_audio_duration(self, audio: str) -> float:
        """Lấy thời lượng audio tính bằng giây"""
        try:
            probe = ffmpeg.probe(audio)
            duration = float(probe['format']['duration'])
            return duration
        except Exception as e:
            logger.warning(f"Không thể lấy thời lượng audio: {e}, dùng ước tính")
            # Dự phòng: ước tính dựa trên kích thước file (rất thô)
            import os
            file_size = os.path.getsize(audio)
            # Giả định ~16kbps cho MP3, nên 2KB mỗi giây
            estimated_duration = file_size / 2000
            return max(1.0, estimated_duration)  # Tối thiểu 1 giây

    def has_audio_stream(self, video: str) -> bool:
        """
        Kiểm tra video có audio stream không

        Args:
            video: Đường dẫn file video

        Returns:
            True nếu video có audio stream, False nếu không
        """
        try:
            probe = ffmpeg.probe(video)
            audio_streams = [s for s in probe.get('streams', []) if s['codec_type'] == 'audio']
            has_audio = len(audio_streams) > 0
            logger.debug(f"Video {video} has_audio={has_audio}")
            return has_audio
        except Exception as e:
            logger.warning(f"Không thể probe audio stream: {e}, giả định không có audio")
            return False
    
    def merge_audio_video(
        self,
        video: str,
        audio: str,
        output: str,
        replace_audio: bool = True,
        audio_volume: float = 1.0,
        video_volume: float = 0.0,
        pad_strategy: str = "freeze",  # "freeze" (freeze last frame) or "black" (black screen)
        auto_adjust_duration: bool = True,  # Automatically adjust video duration to match audio
        duration_tolerance: float = 0.3,  # Tolerance for video being longer than audio (seconds)
    ) -> str:
        """
        Ghép audio với video kèm điều chỉnh thời lượng thông minh

        Tự động xử lý chênh lệch thời lượng giữa video và audio:
        - Nếu video < audio: Đệm video cho khớp audio (tránh màn hình đen)
        - Nếu video > audio (trong dung sai): Giữ nguyên (chấp nhận được)
        - Nếu video > audio (vượt dung sai): Cắt video cho khớp audio

        Tự động xử lý video có hoặc không có audio stream.
        - Nếu video không có audio: thêm track audio
        - Nếu video có audio và replace_audio=True: thay thế bằng audio mới
        - Nếu video có audio và replace_audio=False: trộn cả hai track audio

        Args:
            video: Đường dẫn file video
            audio: Đường dẫn file audio
            output: Đường dẫn file video output
            replace_audio: Nếu True, thay thế audio của video; nếu False, trộn với audio gốc
            audio_volume: Âm lượng audio mới (0.0 đến 1.0+)
            video_volume: Âm lượng audio gốc của video (0.0 đến 1.0+)
                         Chỉ dùng khi replace_audio=False
            pad_strategy: Chiến lược đệm video nếu audio dài hơn
                         - "freeze": Đóng băng frame cuối (mặc định)
                         - "black": Lấp đầy bằng màn hình đen
            auto_adjust_duration: Bật điều chỉnh thời lượng thông minh (mặc định: True)
            duration_tolerance: Dung sai cho việc video dài hơn audio (giây, mặc định: 0.3)
                              Video trong khoảng dung sai này sẽ không bị cắt

        Returns:
            Đường dẫn file video output

        Raises:
            RuntimeError: Nếu thực thi FFmpeg thất bại

        Lưu ý:
            - Dùng thời lượng dài hơn giữa video và audio
            - Khi audio dài hơn, video được đệm dùng pad_strategy
            - Khi video dài hơn, audio được lặp hoặc kéo dài
            - Tự động phát hiện video có audio không
            - Khi video không có tiếng, audio được thêm bất kể replace_audio
            - Khi replace_audio=True và video có audio, audio gốc bị xoá
            - Khi replace_audio=False và video có audio, audio gốc và mới được trộn
        """
        # Lấy thời lượng video và audio
        video_duration = self._get_video_duration(video)
        audio_duration = self._get_audio_duration(audio)

        logger.info(f"Thời lượng video: {video_duration:.2f}s, Thời lượng audio: {audio_duration:.2f}s")

        # Điều chỉnh thời lượng thông minh (nếu được bật)
        if auto_adjust_duration:
            diff = video_duration - audio_duration

            if diff < 0:
                # Video ngắn hơn audio → Phải đệm để tránh màn hình đen
                logger.warning(f"⚠️ Video ngắn hơn audio {abs(diff):.2f}s, cần đệm")
                video = self._pad_video_to_duration(video, audio_duration, pad_strategy)
                video_duration = audio_duration  # Cập nhật thời lượng sau khi đệm
                logger.info(f"📌 Đã đệm video tới {audio_duration:.2f}s")

            elif diff > duration_tolerance:
                # Video dài hơn audio đáng kể → Cắt
                logger.info(f"⚠️ Video dài hơn audio {diff:.2f}s (dung sai: {duration_tolerance}s)")
                video = self._trim_video_to_duration(video, audio_duration)
                video_duration = audio_duration  # Cập nhật thời lượng sau khi cắt
                logger.info(f"✂️ Đã cắt video tới {audio_duration:.2f}s")

            else:  # 0 <= diff <= duration_tolerance
                # Video dài hơn một chút nhưng trong dung sai → Giữ nguyên
                logger.info(f"✅ Thời lượng chấp nhận được: video={video_duration:.2f}s, audio={audio_duration:.2f}s (chênh={diff:.2f}s)")

        # Xác định thời lượng đích (max của cả hai)
        target_duration = max(video_duration, audio_duration)
        logger.info(f"Thời lượng output đích: {target_duration:.2f}s")

        # Kiểm tra video có audio stream không
        video_has_audio = self.has_audio_stream(video)

        # Chuẩn bị video stream (có thể có đệm)
        input_video = ffmpeg.input(video)
        video_stream = input_video.video

        # Đệm video nếu audio dài hơn
        if audio_duration > video_duration:
            pad_duration = audio_duration - video_duration
            logger.info(f"Audio dài hơn, đệm video {pad_duration:.2f}s bằng chiến lược '{pad_strategy}'")

            if pad_strategy == "freeze":
                # Đóng băng frame cuối: filter tpad
                video_stream = video_stream.filter('tpad', stop_mode='clone', stop_duration=pad_duration)
            else:  # black
                # Sinh frame đen cho thời lượng đệm
                # Lấy thuộc tính video
                probe = ffmpeg.probe(video)
                video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
                width = int(video_info['width'])
                height = int(video_info['height'])
                fps_str = video_info['r_frame_rate']
                fps_num, fps_den = map(int, fps_str.split('/'))
                fps = fps_num / fps_den if fps_den != 0 else 30
                
                # Tạo video đen để đệm
                black_video_path = self._get_unique_temp_path("black_pad", os.path.basename(output))
                black_input = ffmpeg.input(
                    f'color=c=black:s={width}x{height}:r={fps}',
                    f='lavfi',
                    t=pad_duration
                )

                # Ghép video gốc với phần đệm đen
                video_stream = ffmpeg.concat(video_stream, black_input.video, v=1, a=0)

        # Chuẩn bị audio stream (đệm nếu cần để khớp thời lượng đích)
        input_audio = ffmpeg.input(audio)
        audio_stream = input_audio.audio.filter('volume', audio_volume)

        # Đệm audio bằng im lặng nếu video dài hơn
        if video_duration > audio_duration:
            pad_duration = video_duration - audio_duration
            logger.info(f"Video dài hơn, đệm audio bằng {pad_duration:.2f}s im lặng")
            # Dùng apad để thêm im lặng ở cuối
            audio_stream = audio_stream.filter('apad', whole_dur=target_duration)

        if not video_has_audio:
            logger.info(f"Video không có audio stream, đang thêm track audio")
            # Video không có tiếng, chỉ cần thêm audio
            try:
                (
                    ffmpeg
                    .output(
                        video_stream,
                        audio_stream,
                        output,
                        vcodec='libx264',  # Re-encode video nếu được đệm
                        acodec='aac',
                        audio_bitrate='192k'
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )

                logger.success(f"Đã thêm audio vào video không tiếng: {output}")
                return output
            except ffmpeg.Error as e:
                error_msg = e.stderr.decode() if e.stderr else str(e)
                logger.error(f"Lỗi FFmpeg khi thêm audio vào video không tiếng: {error_msg}")
                raise RuntimeError(f"Không thể thêm audio vào video: {error_msg}")

        # Video có audio, tiếp tục ghép
        logger.info(f"Đang ghép audio với video (replace={replace_audio})")

        try:
            if replace_audio:
                # Thay thế audio: chỉ dùng audio mới, bỏ qua audio gốc
                (
                    ffmpeg
                    .output(
                        video_stream,
                        audio_stream,
                        output,
                        vcodec='libx264',  # Re-encode video nếu được đệm
                        acodec='aac',
                        audio_bitrate='192k'
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )
            else:
                # Trộn audio: kết hợp audio gốc và audio mới
                mixed_audio = ffmpeg.filter(
                    [
                        input_video.audio.filter('volume', video_volume),
                        audio_stream
                    ],
                    'amix',
                    inputs=2,
                    duration='longest'  # Dùng audio dài nhất
                )

                (
                    ffmpeg
                    .output(
                        video_stream,
                        mixed_audio,
                        output,
                        vcodec='libx264',  # Re-encode video nếu được đệm
                        acodec='aac',
                        audio_bitrate='192k'
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True)
                )

            logger.success(f"Đã ghép audio thành công: {output}")
            return output
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Lỗi ghép FFmpeg: {error_msg}")
            raise RuntimeError(f"Không thể ghép audio và video: {error_msg}")
    
    def overlay_image_on_video(
        self,
        video: str,
        overlay_image: str,
        output: str,
        scale_mode: str = "contain"
    ) -> str:
        """
        Phủ một ảnh trong suốt lên trên video

        Args:
            video: Đường dẫn file video gốc
            overlay_image: Đường dẫn ảnh overlay trong suốt (vd: HTML đã render với nền trong suốt)
            output: Đường dẫn file video output
            scale_mode: Cách scale video gốc cho khớp kích thước overlay
                - "contain": Scale video vừa khít trong overlay (letterbox/pillarbox)
                - "cover": Scale video phủ kín overlay (có thể bị cắt)
                - "stretch": Kéo giãn video đúng kích thước overlay

        Returns:
            Đường dẫn file video output

        Raises:
            RuntimeError: Nếu thực thi FFmpeg thất bại

        Lưu ý:
            - Ảnh overlay phải có nền trong suốt
            - Video được scale cho khớp kích thước overlay dựa trên scale_mode
            - Kích thước video cuối khớp với kích thước ảnh overlay
            - Codec video được re-encode để hỗ trợ overlay
        """
        logger.info(f"Đang phủ ảnh lên video (scale_mode={scale_mode})")
        
        try:
            # Lấy kích thước ảnh overlay
            overlay_probe = ffmpeg.probe(overlay_image)
            overlay_stream = next(s for s in overlay_probe['streams'] if s['codec_type'] == 'video')
            overlay_width = int(overlay_stream['width'])
            overlay_height = int(overlay_stream['height'])

            logger.debug(f"Kích thước overlay: {overlay_width}x{overlay_height}")

            input_video = ffmpeg.input(video)
            input_overlay = ffmpeg.input(overlay_image)

            # Scale video để khớp kích thước overlay dùng scale_mode
            if scale_mode == "contain":
                # Scale vừa khít (letterbox/pillarbox nếu tỉ lệ khác nhau)
                # Dùng filter scale với force_original_aspect_ratio=decrease và pad ở giữa
                scaled_video = (
                    input_video
                    .filter('scale', overlay_width, overlay_height, force_original_aspect_ratio='decrease')
                    .filter('pad', overlay_width, overlay_height, '(ow-iw)/2', '(oh-ih)/2', color='black')
                )
            elif scale_mode == "cover":
                # Scale phủ kín (cắt nếu tỉ lệ khác nhau)
                scaled_video = (
                    input_video
                    .filter('scale', overlay_width, overlay_height, force_original_aspect_ratio='increase')
                    .filter('crop', overlay_width, overlay_height)
                )
            else:  # stretch
                # Kéo giãn đúng kích thước
                scaled_video = input_video.filter('scale', overlay_width, overlay_height)

            # Phủ ảnh trong suốt lên trên video đã scale
            output_stream = ffmpeg.overlay(scaled_video, input_overlay)

            (
                ffmpeg
                .output(output_stream, output,
                        vcodec='libx264',
                        pix_fmt='yuv420p',
                        preset='medium',
                        crf=23)
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            logger.success(f"Đã phủ ảnh lên video: {output}")
            return output
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Lỗi FFmpeg overlay: {error_msg}")
            raise RuntimeError(f"Không thể phủ ảnh lên video: {error_msg}")
    
    def create_video_from_image(
        self,
        image: str,
        audio: str,
        output: str,
        fps: int = 30,
    ) -> str:
        """
        Tạo video từ ảnh tĩnh và audio

        Args:
            image: Đường dẫn file ảnh
            audio: Đường dẫn file audio
            output: Đường dẫn video output
            fps: Số khung hình mỗi giây

        Returns:
            Đường dẫn video output

        Raises:
            RuntimeError: Nếu thực thi FFmpeg thất bại

        Lưu ý:
            - Ảnh được hiển thị như frame tĩnh trong suốt thời lượng audio
            - Thời lượng video khớp với thời lượng audio
            - Hữu ích cho việc tạo segment video từ frame của storyboard

        Ví dụ:
            >>> compositor.create_video_from_image(
            ...     "frame.png",
            ...     "narration.mp3",
            ...     "segment.mp4"
            ... )
        """
        logger.info("Đang tạo video từ ảnh và audio")

        try:
            # Lấy thời lượng audio để đảm bảo thời lượng video khớp chính xác
            probe = ffmpeg.probe(audio)
            audio_duration = float(probe['format']['duration'])
            logger.debug(f"Thời lượng audio: {audio_duration:.3f}s")

            # Input ảnh với loop (loop=1 nghĩa là lặp vô hạn)
            # Dùng framerate để đặt framerate input
            input_image = ffmpeg.input(image, loop=1, framerate=fps)
            input_audio = ffmpeg.input(audio)

            # Kết hợp ảnh và audio
            # Dùng -t để đặt rõ thời lượng video = thời lượng audio
            (
                ffmpeg
                .output(
                    input_image,
                    input_audio,
                    output,
                    t=audio_duration,  # Buộc thời lượng video khớp chính xác audio
                    vcodec='libx264',
                    acodec='aac',
                    pix_fmt='yuv420p',
                    audio_bitrate='192k',
                    preset='medium',
                    crf=23,
                    **{'b:v': '2M'}  # Bitrate video
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            logger.success(f"Đã tạo video từ ảnh: {output} (thời lượng: {audio_duration:.3f}s)")
            return output
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Lỗi FFmpeg khi tạo video từ ảnh: {error_msg}")
            raise RuntimeError(f"Không thể tạo video từ ảnh: {error_msg}")
    
    def add_bgm(
        self,
        video: str,
        bgm: str,
        output: str,
        bgm_volume: float = 0.3,
        loop: bool = True,
        fade_in: float = 0.0,
        fade_out: float = 0.0,
    ) -> str:
        """
        Thêm nhạc nền vào video

        Args:
            video: Đường dẫn file video
            bgm: Đường dẫn file nhạc nền
            output: Đường dẫn file video output
            bgm_volume: Âm lượng BGM tương đối so với gốc (0.0 đến 1.0+)
            loop: Nếu True, lặp BGM cho khớp thời lượng video
            fade_in: Thời lượng fade-in BGM (giây)
            fade_out: Thời lượng fade-out BGM (giây, chưa triển khai)

        Returns:
            Đường dẫn file video output

        Raises:
            RuntimeError: Nếu thực thi FFmpeg thất bại

        Lưu ý:
            - BGM được trộn với audio gốc của video
            - Nếu loop=True, BGM lặp tới khi video kết thúc
            - Hiệu ứng fade chỉ áp dụng cho BGM
        """
        logger.info(f"Đang thêm BGM vào video (âm lượng={bgm_volume}, loop={loop})")

        try:
            input_video = ffmpeg.input(video)

            # Cấu hình input BGM với loop nếu cần
            bgm_input = ffmpeg.input(
                bgm,
                stream_loop=-1 if loop else 0  # -1 = lặp vô hạn
            )

            # Áp dụng điều chỉnh âm lượng cho BGM
            bgm_audio = bgm_input.audio.filter('volume', bgm_volume)

            # Áp dụng hiệu ứng fade nếu được chỉ định
            if fade_in > 0:
                bgm_audio = bgm_audio.filter('afade', type='in', duration=fade_in)
            # Lưu ý: fade_out ở cuối yêu cầu biết thời lượng, điều này phức tạp
            # Hiện tại bỏ qua fade_out trong implementation này
            # Một implementation nâng cao hơn sẽ cần:
            # 1. Lấy thời lượng video
            # 2. Tính thời điểm bắt đầu fade_out
            # 3. Áp dụng filter fade với start_time cụ thể

            # Trộn audio gốc với BGM
            mixed_audio = ffmpeg.filter(
                [input_video.audio, bgm_audio],
                'amix',
                inputs=2,
                duration='first'  # Dùng thời lượng của video
            )

            (
                ffmpeg
                .output(
                    input_video.video,
                    mixed_audio,
                    output,
                    vcodec='copy',
                    acodec='aac',
                    audio_bitrate='192k'
                )
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True)
            )

            logger.success(f"Đã thêm BGM thành công: {output}")
            return output
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Lỗi FFmpeg BGM: {error_msg}")
            raise RuntimeError(f"Không thể thêm BGM: {error_msg}")
    
    def _add_bgm_to_video(
        self,
        video: str,
        bgm_path: str,
        output: str,
        volume: float = 0.2,
        mode: Literal["once", "loop"] = "loop"
    ) -> str:
        """
        Helper nội bộ để thêm BGM vào video kèm phân giải đường dẫn

        Args:
            video: Đường dẫn file video
            bgm_path: Đường dẫn BGM (có thể là tên preset hoặc đường dẫn tuỳ chỉnh)
            output: Đường dẫn file output
            volume: Âm lượng BGM (0.0-1.0)
            mode: "once" hoặc "loop"

        Returns:
            Đường dẫn video output

        Raises:
            FileNotFoundError: Nếu không tìm thấy file BGM
        """
        # Phân giải đường dẫn BGM (raise FileNotFoundError nếu không tìm thấy)
        resolved_bgm = self._resolve_bgm_path(bgm_path)

        # Thêm BGM bằng method có sẵn
        loop = (mode == "loop")
        return self.add_bgm(
            video=video,
            bgm=resolved_bgm,
            output=output,
            bgm_volume=volume,
            loop=loop,
            fade_in=0.0
        )
    
    def _get_unique_temp_path(self, prefix: str, original_filename: str) -> str:
        """
        Sinh đường dẫn file tạm duy nhất để tránh xung đột khi chạy song song

        Args:
            prefix: Tiền tố cho file tạm (vd: "trimmed", "padded", "black_pad")
            original_filename: Tên file gốc để giữ trong đường dẫn tạm

        Returns:
            Đường dẫn file tạm duy nhất theo định dạng: temp/{prefix}_{uuid}_{original_filename}

        Ví dụ:
            >>> self._get_unique_temp_path("trimmed", "video.mp4")
            >>> # Trả về: "temp/trimmed_a3f2d8c1_video.mp4"
        """
        from pixelle_video.utils.os_util import get_temp_path
        
        unique_id = uuid.uuid4().hex[:8]
        return get_temp_path(f"{prefix}_{unique_id}_{original_filename}")
    
    def _resolve_bgm_path(self, bgm_path: str) -> str:
        """
        Phân giải đường dẫn BGM (tên file hoặc đường dẫn tuỳ chỉnh) kèm hỗ trợ ghi đè tuỳ chỉnh

        Thứ tự ưu tiên tìm kiếm:
            1. Đường dẫn trực tiếp (tuyệt đối hoặc tương đối)
            2. data/bgm/{filename} (tuỳ chỉnh)
            3. bgm/{filename} (mặc định)

        Args:
            bgm_path: Có thể là:
                - Tên file kèm phần mở rộng (vd: "default.mp3", "happy.mp3"): tự động phân giải từ bgm/ hoặc data/bgm/
                - Đường dẫn file tuỳ chỉnh (tuyệt đối hoặc tương đối)

        Returns:
            Đường dẫn tuyệt đối đã phân giải

        Raises:
            FileNotFoundError: Nếu không tìm thấy file BGM
        """
        # Thử đường dẫn trực tiếp trước (tuyệt đối hoặc tương đối)
        if os.path.exists(bgm_path):
            return os.path.abspath(bgm_path)

        # Thử như tên file trong các thư mục resource (tuỳ chỉnh > mặc định)
        if resource_exists("bgm", bgm_path):
            return get_resource_path("bgm", bgm_path)

        # Không tìm thấy - cung cấp thông báo lỗi hữu ích
        tried_paths = [
            os.path.abspath(bgm_path),
            f"data/bgm/{bgm_path} hoặc bgm/{bgm_path}"
        ]

        # Liệt kê các file BGM có sẵn
        available_bgm = self._list_available_bgm()
        available_msg = f"\n  File BGM có sẵn: {', '.join(available_bgm)}" if available_bgm else ""

        raise FileNotFoundError(
            f"Không tìm thấy file BGM: '{bgm_path}'\n"
            f"  Đã thử đường dẫn:\n"
            f"    1. {tried_paths[0]}\n"
            f"    2. {tried_paths[1]}"
            f"{available_msg}"
        )

    def _list_available_bgm(self) -> list[str]:
        """
        Liệt kê các file BGM có sẵn (gộp từ bgm/ và data/bgm/)

        Returns:
            Danh sách tên file (kèm phần mở rộng), đã sắp xếp
        """
        try:
            # Dùng resource API để lấy danh sách đã gộp
            all_files = list_resource_files("bgm")

            # Chỉ lọc các file audio
            audio_extensions = ('.mp3', '.wav', '.ogg', '.flac', '.m4a', '.aac')
            return sorted([f for f in all_files if f.lower().endswith(audio_extensions)])
        except Exception as e:
            logger.warning(f"Không thể liệt kê file BGM: {e}")
            return []

    def _trim_video_to_duration(self, video: str, target_duration: float) -> str:
        """
        Cắt video về thời lượng được chỉ định

        Args:
            video: Đường dẫn file video đầu vào
            target_duration: Thời lượng đích tính bằng giây

        Returns:
            Đường dẫn video đã cắt (file tạm)

        Raises:
            RuntimeError: Nếu thực thi FFmpeg thất bại
        """
        output = self._get_unique_temp_path("trimmed", os.path.basename(video))

        try:
            # Dùng stream copy khi có thể để cắt nhanh
            (
                ffmpeg
                .input(video, t=target_duration)
                .output(output, vcodec='copy', acodec='copy' if self.has_audio_stream(video) else 'copy')
                .overwrite_output()
                .run(capture_stdout=True, capture_stderr=True, quiet=True)
            )
            return output
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Lỗi FFmpeg khi cắt video: {error_msg}")
            raise RuntimeError(f"Không thể cắt video: {error_msg}")

    def _pad_video_to_duration(self, video: str, target_duration: float, pad_strategy: str = "freeze") -> str:
        """
        Đệm video về thời lượng được chỉ định bằng cách kéo dài frame cuối hoặc thêm frame đen

        Args:
            video: Đường dẫn file video đầu vào
            target_duration: Thời lượng đích tính bằng giây
            pad_strategy: Chiến lược đệm - "freeze" (đóng băng frame cuối) hoặc "black" (màn hình đen)

        Returns:
            Đường dẫn video đã đệm (file tạm)

        Raises:
            RuntimeError: Nếu thực thi FFmpeg thất bại
        """
        output = self._get_unique_temp_path("padded", os.path.basename(video))
        
        video_duration = self._get_video_duration(video)
        pad_duration = target_duration - video_duration
        
        if pad_duration <= 0:
            # Không cần đệm, trả về gốc
            return video

        try:
            input_video = ffmpeg.input(video)
            video_stream = input_video.video

            if pad_strategy == "freeze":
                # Đóng băng frame cuối bằng filter tpad
                video_stream = video_stream.filter('tpad', stop_mode='clone', stop_duration=pad_duration)

                # Output kèm re-encode (tpad yêu cầu)
                (
                    ffmpeg
                    .output(
                        video_stream,
                        output,
                        vcodec='libx264',
                        preset='fast',
                        crf=23
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )
            else:  # black
                # Sinh frame đen cho thời lượng đệm
                # Lấy thuộc tính video
                probe = ffmpeg.probe(video)
                video_info = next(s for s in probe['streams'] if s['codec_type'] == 'video')
                width = int(video_info['width'])
                height = int(video_info['height'])
                fps_str = video_info['r_frame_rate']
                fps_num, fps_den = map(int, fps_str.split('/'))
                fps = fps_num / fps_den if fps_den != 0 else 30

                # Tạo video đen để đệm
                black_input = ffmpeg.input(
                    f'color=c=black:s={width}x{height}:r={fps}',
                    f='lavfi',
                    t=pad_duration
                )

                # Ghép video gốc với phần đệm đen
                video_stream = ffmpeg.concat(video_stream, black_input.video, v=1, a=0)

                (
                    ffmpeg
                    .output(
                        video_stream,
                        output,
                        vcodec='libx264',
                        preset='fast',
                        crf=23
                    )
                    .overwrite_output()
                    .run(capture_stdout=True, capture_stderr=True, quiet=True)
                )
            
            return output
        except ffmpeg.Error as e:
            error_msg = e.stderr.decode() if e.stderr else str(e)
            logger.error(f"Lỗi FFmpeg khi đệm video: {error_msg}")
            raise RuntimeError(f"Không thể đệm video: {error_msg}")

