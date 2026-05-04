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
Trang Lịch sử - Xem lịch sử sinh video và quản lý tác vụ
"""

import sys
from pathlib import Path
from datetime import datetime
import os

# Thêm thư mục gốc dự án vào sys.path
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st
from loguru import logger

from web.state.session import init_session_state, init_i18n, get_pixelle_video
from web.components.header import render_header
from web.i18n import tr
from web.utils.async_helpers import run_async

# Cấu hình trang
st.set_page_config(
    page_title="Lịch sử - Pixelle-Video",
    page_icon="📚",
    layout="wide",
)


def format_duration(seconds: float) -> str:
    """Định dạng khoảng thời gian (giây) thành chuỗi dễ đọc"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        secs = int(seconds % 60)
        return f"{minutes}m {secs}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"


def format_file_size(bytes_size: int) -> str:
    """Định dạng kích thước file (byte) thành chuỗi dễ đọc"""
    if bytes_size < 1024:
        return f"{bytes_size}B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size / 1024:.1f}KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size / 1024 / 1024:.1f}MB"
    else:
        return f"{bytes_size / 1024 / 1024 / 1024:.2f}GB"


def format_datetime(iso_string: str) -> str:
    """Định dạng chuỗi datetime ISO thành định dạng dễ đọc"""
    try:
        dt = datetime.fromisoformat(iso_string)
        return dt.strftime("%m-%d %H:%M")
    except:
        return iso_string


def truncate_text(text: str, max_length: int = 60) -> str:
    """Cắt ngắn text về độ dài tối đa"""
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def render_sidebar_controls(pixelle_video):
    """Render sidebar với thống kê và bộ lọc"""
    with st.sidebar:
        # Thống kê
        st.markdown(f"**📊 {tr('history.total_tasks')}**")
        stats = run_async(pixelle_video.history.get_statistics())

        col1, col2 = st.columns(2)
        with col1:
            st.metric(tr("history.completed_count"), stats.get("completed", 0))
        with col2:
            st.metric(tr("history.failed_count"), stats.get("failed", 0))

        st.divider()

        # Bộ lọc
        st.markdown(f"**🔍 {tr('history.filter_status')}**")
        status_options = {
            "all": tr("history.status_all"),
            "completed": tr("history.status_completed"),
            "failed": tr("history.status_failed"),
            "running": tr("history.status_running"),
            "pending": tr("history.status_pending"),
        }
        
        selected_status = st.selectbox(
            tr("history.filter_status"),
            options=list(status_options.keys()),
            format_func=lambda x: status_options[x],
            key="filter_status",
            label_visibility="collapsed"
        )
        
        filter_status = None if selected_status == "all" else selected_status

        # Sắp xếp
        st.markdown(f"**📊 {tr('history.sort_by')}**")
        
        sort_options = {
            "created_at": tr("history.sort_created_at"),
            "completed_at": tr("history.sort_completed_at"),
            "title": tr("history.sort_title"),
            "duration": tr("history.sort_duration"),
        }
        
        sort_by = st.selectbox(
            tr("history.sort_by"),
            options=list(sort_options.keys()),
            format_func=lambda x: sort_options[x],
            key="sort_by",
            label_visibility="collapsed"
        )
        
        sort_order_options = {
            "desc": tr("history.sort_order_desc"),
            "asc": tr("history.sort_order_asc"),
        }
        
        sort_order = st.radio(
            "Thứ tự sắp xếp",
            options=list(sort_order_options.keys()),
            format_func=lambda x: sort_order_options[x],
            key="sort_order",
            label_visibility="collapsed",
            horizontal=True
        )

        # Số bản ghi mỗi trang
        page_size = st.selectbox(
            tr("history.page_size"),
            options=[15, 30, 60],
            index=0,
            key="page_size"
        )

        return filter_status, sort_by, sort_order, page_size


def render_grid_task_card(task: dict, pixelle_video):
    """Render thẻ task dạng grid gọn"""
    task_id = task["task_id"]
    title = task.get("title", "Không có tiêu đề")
    status = task.get("status", "unknown")
    created_at = task.get("created_at", "")
    duration = task.get("duration", 0)
    n_frames = task.get("n_frames", 0)
    video_path = task.get("video_path", "")

    # Nhãn trạng thái
    status_map = {
        "completed": "✅",
        "failed": "❌",
        "running": "⏳",
        "pending": "⏸️",
    }
    status_icon = status_map.get(status, "❓")

    # Lấy nội dung input
    detail = run_async(pixelle_video.history.get_task_detail(task_id))
    input_text = ""
    if detail and detail.get("metadata"):
        input_params = detail["metadata"].get("input", {})
        input_text = input_params.get("text", "")

    # Container thẻ
    with st.container():
        # Xem trước video ở trên cùng
        if video_path and os.path.exists(video_path):
            st.video(video_path, autoplay=False, loop=False, muted=False)
        else:
            st.markdown(
                f"<div style='background: #f0f0f0; height: 180px; display: flex; align-items: center; "
                f"justify-content: center; border-radius: 4px; font-size: 48px;'>📹</div>",
                unsafe_allow_html=True
            )

        # Tiêu đề + Trạng thái (gọn) - hiển thị tiêu đề thực tế của task
        st.markdown(f"**{status_icon} {truncate_text(title, 50)}**")

        # Nội dung input (rất ngắn)
        if input_text:
            st.caption(truncate_text(input_text, 60))

        # Thông tin meta (một dòng)
        st.caption(f"🕒 {format_datetime(created_at)} | ⏱️ {format_duration(duration)} | 🎬 {n_frames}")

        # Các nút thao tác (gọn, 3 cột)
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("👁️", key=f"view_{task_id}", help=tr("history.task_card.view_detail"), use_container_width=True):
                st.session_state[f"detail_{task_id}"] = True
                st.rerun()

        with col2:
            if video_path and os.path.exists(video_path):
                with open(video_path, "rb") as f:
                    st.download_button(
                        "⬇️",
                        data=f,
                        file_name=f"{title}.mp4",
                        mime="video/mp4",
                        key=f"download_{task_id}",
                        help=tr("history.task_card.download"),
                        use_container_width=True
                    )
            else:
                st.button("⬇️", key=f"download_disabled_{task_id}", disabled=True, use_container_width=True)

        with col3:
            if st.button("🗑️", key=f"delete_{task_id}", help=tr("history.task_card.delete"), use_container_width=True):
                st.session_state[f"confirm_delete_{task_id}"] = True
                st.rerun()

        # Xác nhận xoá (hiển thị giống modal)
        if st.session_state.get(f"confirm_delete_{task_id}", False):
            st.warning("⚠️ Xác nhận xoá?")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅", key=f"confirm_yes_{task_id}", use_container_width=True):
                    try:
                        success = run_async(pixelle_video.history.delete_task(task_id))
                        if success:
                            st.success(tr("history.action.delete_success"))
                            st.session_state[f"confirm_delete_{task_id}"] = False
                            st.rerun()
                        else:
                            st.error("Xoá thất bại")
                    except Exception as e:
                        st.error(f"Xoá thất bại: {str(e)}")
            with col2:
                if st.button("❌", key=f"confirm_no_{task_id}", use_container_width=True):
                    st.session_state[f"confirm_delete_{task_id}"] = False
                    st.rerun()


def render_task_detail_modal(task_id: str, pixelle_video):
    """Render chi tiết task theo bố cục ba cột"""
    detail = run_async(pixelle_video.history.get_task_detail(task_id))

    if not detail:
        st.error("Không tìm thấy task")
        return

    metadata = detail["metadata"]
    storyboard = detail["storyboard"]

    # Nút đóng ở phía trên
    if st.button("❌ " + tr("history.detail.close"), key=f"close_detail_top_{task_id}"):
        st.session_state[f"detail_{task_id}"] = False
        st.rerun()

    st.markdown(f"**{tr('history.detail.modal_title')}**")
    st.caption(f"{tr('history.detail.task_id')}: {task_id}")

    # Bố cục ba cột
    col_input, col_storyboard, col_video = st.columns([1, 1, 1])

    # Cột trái: Input và cấu hình
    with col_input:
        st.markdown(f"**📝 {tr('history.detail.input_params')}**")

        input_params = metadata.get("input", {})

        # Hiển thị các tham số input
        st.markdown(f"**{tr('history.detail.mode')}:** {input_params.get('mode', 'N/A')}")
        st.markdown(f"**{tr('history.detail.n_scenes')}:** {input_params.get('n_scenes', 'N/A')}")
        st.markdown(f"**{tr('history.detail.tts_mode')}:** {input_params.get('tts_inference_mode', 'N/A')}")
        st.markdown(f"**{tr('history.detail.voice')}:** {input_params.get('tts_voice', 'N/A')}")

        # Text input
        with st.expander(tr("history.detail.text"), expanded=True):
            st.text_area(
                "Nội dung nhập",
                value=input_params.get('text', 'N/A'),
                height=200,
                disabled=True,
                label_visibility="collapsed"
            )

    # Cột giữa: Các phân cảnh storyboard
    with col_storyboard:
        st.markdown(f"**🎬 {tr('history.detail.storyboard')}**")

        if storyboard and storyboard.frames:
            for frame in storyboard.frames:
                with st.expander(f"{tr('history.detail.frame')} {frame.index + 1}", expanded=False):
                    st.markdown(f"**{tr('history.detail.narration')}:**")
                    st.caption(frame.narration)

                    if frame.image_prompt:
                        st.markdown(f"**{tr('history.detail.image_prompt')}:**")
                        st.caption(frame.image_prompt)

                    # Hiển thị xem trước phân cảnh (nhỏ)
                    col1, col2 = st.columns(2)
                    with col1:
                        if frame.composed_image_path and os.path.exists(frame.composed_image_path):
                            st.image(frame.composed_image_path)
                        elif frame.image_path and os.path.exists(frame.image_path):
                            st.image(frame.image_path)
                    with col2:
                        if frame.video_segment_path and os.path.exists(frame.video_segment_path):
                            st.video(frame.video_segment_path)

                    # Trình phát audio (gọn)
                    if frame.audio_path and os.path.exists(frame.audio_path):
                        st.audio(frame.audio_path)
        else:
            st.info("Không có dữ liệu storyboard")

    # Cột phải: Video cuối cùng
    with col_video:
        st.markdown(f"**🎥 {tr('info.video_information')}**")

        video_path = metadata.get("result", {}).get("video_path")
        if video_path and os.path.exists(video_path):
            st.video(video_path)

            # Thông tin video
            result = metadata.get("result", {})
            st.markdown(f"**{tr('info.duration')}:** {format_duration(result.get('duration', 0))}")
            st.markdown(f"**{tr('info.frames')}:** {result.get('n_frames', 0)}")
            st.markdown(f"**{tr('info.file_size')}:** {format_file_size(result.get('file_size', 0))}")

            # Nút tải xuống
            with open(video_path, "rb") as f:
                # Lấy title từ input (đã bao gồm tiêu đề được sinh)
                title = metadata.get("input", {}).get("title", "video")
                if not title:
                    title = "video"
                st.download_button(
                    tr("history.detail.download_video"),
                    data=f,
                    file_name=f"{title}.mp4",
                    mime="video/mp4",
                    use_container_width=True
                )
        else:
            st.warning("Không tìm thấy file video")

    st.divider()

    # Nút đóng ở phía dưới
    if st.button("❌ " + tr("history.detail.close"), key=f"close_detail_bottom_{task_id}"):
        st.session_state[f"detail_{task_id}"] = False
        st.rerun()


def main():
    """Điểm khởi chạy chính cho trang Lịch sử"""
    # Khởi tạo
    init_session_state()
    init_i18n()

    # Render header
    render_header()

    # Khởi tạo Pixelle-Video
    pixelle_video = get_pixelle_video()

    # Sidebar: Thống kê + Bộ lọc
    filter_status, sort_by, sort_order, page_size = render_sidebar_controls(pixelle_video)

    # Khởi tạo phân trang trong session state
    if "history_page" not in st.session_state:
        st.session_state.history_page = 1

    # Kiểm tra có cần hiển thị view chi tiết không
    show_detail_for = None
    for key in st.session_state.keys():
        if key.startswith("detail_") and st.session_state[key]:
            show_detail_for = key.replace("detail_", "")
            break

    # Nếu đang xem chi tiết, render nó
    if show_detail_for:
        render_task_detail_modal(show_detail_for, pixelle_video)
        return

    # Ngược lại, hiển thị danh sách dạng lưới
    # Lấy danh sách task
    result = run_async(pixelle_video.history.get_task_list(
        page=st.session_state.history_page,
        page_size=page_size,
        status=filter_status,
        sort_by=sort_by,
        sort_order=sort_order
    ))

    tasks = result["tasks"]
    total = result["total"]
    total_pages = result["total_pages"]

    # Tiêu đề trang kèm số lượng
    st.markdown(f"##### 📚 {tr('history.page_title')} ({total})")

    # Hiển thị các thẻ task theo bố cục lưới (4 cột)
    if not tasks:
        st.info(tr("history.no_tasks"))
    else:
        # Bố cục lưới: 4 thẻ mỗi hàng
        CARDS_PER_ROW = 4

        # Xử lý task theo lô CARDS_PER_ROW
        for i in range(0, len(tasks), CARDS_PER_ROW):
            cols = st.columns(CARDS_PER_ROW)

            # Lấp đầy mỗi cột với một thẻ task
            for j in range(CARDS_PER_ROW):
                task_idx = i + j
                if task_idx < len(tasks):
                    with cols[j]:
                        render_grid_task_card(tasks[task_idx], pixelle_video)

    # Phân trang
    if total_pages > 1:
        st.divider()
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            if st.button("⬅️ Trước", disabled=st.session_state.history_page == 1, use_container_width=True):
                st.session_state.history_page -= 1
                st.rerun()

        with col2:
            st.markdown(
                f"<div style='text-align: center; padding-top: 8px;'>"
                f"{tr('history.page_info').format(page=st.session_state.history_page, total_pages=total_pages)}"
                f"</div>",
                unsafe_allow_html=True
            )

        with col3:
            if st.button("Sau ➡️", disabled=st.session_state.history_page == total_pages, use_container_width=True):
                st.session_state.history_page += 1
                st.rerun()


if __name__ == "__main__":
    main()
