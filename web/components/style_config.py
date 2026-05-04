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
Component cấu hình style cho web UI (cột giữa)
"""

import os
from pathlib import Path

import streamlit as st
from loguru import logger

from web.i18n import tr, get_language
from web.utils.async_helpers import run_async
from web.utils.streamlit_helpers import check_and_warn_selfhost_workflow
from pixelle_video.config import config_manager


def render_style_config(pixelle_video):
    """Render phần cấu hình style (cột giữa)"""
    # Phần TTS (chuyển từ cột trái sang)
    # ====================================================================
    with st.container(border=True):
        st.markdown(f"**{tr('section.tts')}**")

        with st.expander(tr("help.feature_description"), expanded=False):
            st.markdown(f"**{tr('help.what')}**")
            st.markdown(tr("tts.what"))
            st.markdown(f"**{tr('help.how')}**")
            st.markdown(tr("tts.how"))

        # Lấy cấu hình TTS
        comfyui_config = config_manager.get_comfyui_config()
        tts_config = comfyui_config["tts"]

        # Chọn chế độ inference
        tts_mode = st.radio(
            tr("tts.inference_mode"),
            ["local", "comfyui"],
            horizontal=True,
            format_func=lambda x: tr(f"tts.mode.{x}"),
            index=0 if tts_config.get("inference_mode", "local") == "local" else 1,
            key="tts_inference_mode"
        )

        # Hiển thị gợi ý theo chế độ
        if tts_mode == "local":
            st.caption(tr("tts.mode.local_hint"))
        else:
            st.caption(tr("tts.mode.comfyui_hint"))

        # ================================================================
        # UI cho chế độ Local
        # ================================================================
        if tts_mode == "local":
            # Import cấu hình giọng đọc
            from pixelle_video.tts_voices import EDGE_TTS_VOICES, get_voice_display_name

            # Lấy giọng đã lưu trong config
            local_config = tts_config.get("local", {})
            saved_voice = local_config.get("voice", "zh-CN-YunjianNeural")
            saved_speed = local_config.get("speed", 1.2)

            # Xây danh sách lựa chọn giọng kèm i18n
            voice_options = []
            voice_ids = []
            default_voice_index = 0

            for idx, voice_config in enumerate(EDGE_TTS_VOICES):
                voice_id = voice_config["id"]
                display_name = get_voice_display_name(voice_id, tr, get_language())
                voice_options.append(display_name)
                voice_ids.append(voice_id)

                # Đặt index mặc định nếu khớp với giọng đã lưu
                if voice_id == saved_voice:
                    default_voice_index = idx

            # Bố cục hai cột: Giọng | Tốc độ
            voice_col, speed_col = st.columns([1, 1])

            with voice_col:
                # Bộ chọn giọng
                selected_voice_display = st.selectbox(
                    tr("tts.voice_selector"),
                    voice_options,
                    index=default_voice_index,
                    key="tts_local_voice"
                )

                # Lấy ID giọng thực tế
                selected_voice_index = voice_options.index(selected_voice_display)
                selected_voice = voice_ids[selected_voice_index]

            with speed_col:
                # Thanh trượt tốc độ
                tts_speed = st.slider(
                    tr("tts.speed"),
                    min_value=0.5,
                    max_value=2.0,
                    value=saved_speed,
                    step=0.1,
                    format="%.1fx",
                    key="tts_local_speed"
                )
                st.caption(tr("tts.speed_label", speed=f"{tts_speed:.1f}"))

            # Biến cho việc sinh video
            tts_workflow_key = None
            ref_audio_path = None

        # ================================================================
        # UI cho chế độ ComfyUI
        # ================================================================
        else:  # chế độ comfyui
            # Lấy danh sách TTS workflow khả dụng
            tts_workflows = pixelle_video.tts.list_workflows()

            # Xây danh sách lựa chọn cho selectbox
            tts_workflow_options = [wf["display_name"] for wf in tts_workflows]
            tts_workflow_keys = [wf["key"] for wf in tts_workflows]

            # Mặc định lấy workflow đã lưu nếu có
            default_tts_index = 0
            saved_tts_workflow = tts_config.get("comfyui", {}).get("default_workflow")
            if saved_tts_workflow and saved_tts_workflow in tts_workflow_keys:
                default_tts_index = tts_workflow_keys.index(saved_tts_workflow)

            tts_workflow_display = st.selectbox(
                "TTS Workflow",
                tts_workflow_options if tts_workflow_options else ["Không tìm thấy TTS workflow"],
                index=default_tts_index,
                label_visibility="collapsed",
                key="tts_workflow_select"
            )

            # Lấy key workflow thực tế
            if tts_workflow_options:
                tts_selected_index = tts_workflow_options.index(tts_workflow_display)
                tts_workflow_key = tts_workflow_keys[tts_selected_index]
            else:
                tts_workflow_key = "selfhost/tts_edge.json"  # giá trị fallback

            # Kiểm tra và cảnh báo cho TTS workflow selfhost (tự động hiện popup nếu chưa xác nhận)
            check_and_warn_selfhost_workflow(tts_workflow_key)

            # Tải lên audio tham chiếu (tuỳ chọn, dùng để clone giọng)
            ref_audio_file = st.file_uploader(
                tr("tts.ref_audio"),
                type=["mp3", "wav", "flac", "m4a", "aac", "ogg"],
                help=tr("tts.ref_audio_help"),
                key="ref_audio_upload"
            )

            # Lưu ref_audio đã tải lên vào file tạm nếu có
            ref_audio_path = None
            if ref_audio_file is not None:
                # Trình phát nghe thử (phát trực tiếp file vừa upload)
                st.audio(ref_audio_file)

                # Lưu vào thư mục tạm
                temp_dir = Path("temp")
                temp_dir.mkdir(exist_ok=True)
                ref_audio_path = temp_dir / f"ref_audio_{ref_audio_file.name}"
                with open(ref_audio_path, "wb") as f:
                    f.write(ref_audio_file.getbuffer())

            # Biến cho việc sinh video
            selected_voice = None
            tts_speed = None

        # ================================================================
        # Nghe thử TTS (dùng được cho cả hai chế độ)
        # ================================================================
        with st.expander(tr("tts.preview_title"), expanded=False):
            # Ô nhập text để nghe thử
            preview_text = st.text_input(
                tr("tts.preview_text"),
                value="Xin chào mọi người, đây là một đoạn giọng nói thử nghiệm.",
                placeholder=tr("tts.preview_text_placeholder"),
                key="tts_preview_text"
            )

            # Nút nghe thử
            if st.button(tr("tts.preview_button"), key="preview_tts", use_container_width=True):
                with st.spinner(tr("tts.previewing")):
                    try:
                        # Xây tham số TTS theo chế độ
                        tts_params = {
                            "text": preview_text,
                            "inference_mode": tts_mode
                        }

                        if tts_mode == "local":
                            tts_params["voice"] = selected_voice
                            tts_params["speed"] = tts_speed
                        else:  # comfyui
                            tts_params["workflow"] = tts_workflow_key
                            if ref_audio_path:
                                tts_params["ref_audio"] = str(ref_audio_path)

                        audio_path = run_async(pixelle_video.tts(**tts_params))

                        # Phát audio
                        if audio_path:
                            st.success(tr("tts.preview_success"))
                            if os.path.exists(audio_path):
                                st.audio(audio_path, format="audio/mp3")
                            elif audio_path.startswith('http'):
                                st.audio(audio_path)
                            else:
                                st.error("Không thể sinh audio xem trước")

                            # Hiển thị đường dẫn file
                            st.caption(f"📁 {audio_path}")
                        else:
                            st.error("Không thể sinh audio xem trước")
                    except Exception as e:
                        st.error(tr("tts.preview_failed", error=str(e)))
                        logger.exception(e)
    
    # ====================================================================
    # Phần Storyboard Template
    # ====================================================================

    def get_template_preview_path(template_path: str, language: str = "zh_CN") -> str:
        """
        Lấy đường dẫn ảnh xem trước cho một template theo ngôn ngữ.

        Args:
            template_path: Đường dẫn template như "1080x1920/image_default.html"
            language: Mã ngôn ngữ, "zh_CN" hoặc "en"

        Returns:
            Đường dẫn ảnh xem trước trong docs/images/
        """
        # Trích xuất kích thước và tên template từ đường dẫn
        # ví dụ: "1080x1920/image_default.html" -> size="1080x1920", name="image_default"
        path_parts = template_path.split('/')
        if len(path_parts) >= 2:
            size = path_parts[0]  # ví dụ: "1080x1920"
            template_file = path_parts[1]  # ví dụ: "image_default.html"
            template_name = template_file.replace('.html', '')  # ví dụ: "image_default"

            # Xây đường dẫn ảnh xem trước
            # Định dạng: docs/images/{size}/{template_name}.jpg hoặc {template_name}_en.jpg
            # Tiếng Trung dùng preview tiếng Trung, các ngôn ngữ khác dùng preview tiếng Anh để hỗ trợ i18n tốt hơn
            suffix = "" if language == "zh_CN" else "_en"

            # Thử các phần mở rộng ảnh khác nhau
            for ext in ['.jpg', '.png']:
                preview_path = f"docs/images/{size}/{template_name}{suffix}{ext}"
                if os.path.exists(preview_path):
                    return preview_path

            # Phương án dự phòng: thử không kèm hậu tố ngôn ngữ (cho template chỉ có một phiên bản)
            for ext in ['.jpg', '.png']:
                preview_path = f"docs/images/{size}/{template_name}{ext}"
                if os.path.exists(preview_path):
                    return preview_path

        # Nếu không tìm thấy preview, trả về chuỗi rỗng
        return ""
    
    with st.container(border=True):
        st.markdown(f"**{tr('section.template')}**")

        with st.expander(tr("help.feature_description"), expanded=False):
            st.markdown(f"**{tr('help.what')}**")
            st.markdown(tr("template.what"))
            st.markdown(f"**{tr('help.how')}**")
            st.markdown(tr("template.how"))

        # Liên kết xem trước template (theo ngôn ngữ)
        current_lang = get_language()

        # Import các tiện ích template
        from pixelle_video.utils.template_util import get_templates_grouped_by_size_and_type, get_template_type

        # Bộ chọn loại template
        st.markdown(f"**{tr('template.type_selector')}**")

        template_type_options = {
            'static': tr('template.type.static'),
            'image': tr('template.type.image'),
            'video': tr('template.type.video')
        }

        # Radio button bố cục ngang
        selected_template_type = st.radio(
            tr('template.type_selector'),
            options=list(template_type_options.keys()),
            format_func=lambda x: template_type_options[x],
            index=1,  # Mặc định 'image'
            key="template_type_selector",
            label_visibility="collapsed",
            horizontal=True
        )

        # Hiển thị gợi ý theo loại đã chọn (bên dưới radio button)
        if selected_template_type == 'static':
            st.info(tr('template.type.static_hint'))
        elif selected_template_type == 'image':
            st.info(tr('template.type.image_hint'))
        elif selected_template_type == 'video':
            st.info(tr('template.type.video_hint'))

        # Lấy template đã nhóm theo kích thước, lọc theo loại đã chọn
        grouped_templates = get_templates_grouped_by_size_and_type(selected_template_type)

        if not grouped_templates:
            st.warning(f"Không tìm thấy template loại {template_type_options[selected_template_type]}. Vui lòng chọn loại khác hoặc thêm template.")
            st.stop()

        # Xây mapping i18n cho hướng
        ORIENTATION_I18N = {
            'portrait': tr('orientation.portrait'),
            'landscape': tr('orientation.landscape'),
            'square': tr('orientation.square')
        }

        # Lấy template mặc định từ config
        template_config = pixelle_video.config.get("template", {})
        config_default_template = template_config.get("default_template", "1080x1920/image_default.html")

        # Tương thích ngược
        if config_default_template == "1080x1920/default.html":
            config_default_template = "1080x1920/image_default.html"

        # Xác định template mặc định theo từng loại
        type_default_templates = {
            'static': '1080x1920/static_default.html',
            'image': '1080x1920/image_default.html',
            'video': '1080x1920/video_default.html'
        }
        type_specific_default = type_default_templates.get(selected_template_type, config_default_template)

        # Khởi tạo template đã chọn trong session state nếu chưa có
        if 'selected_template' not in st.session_state:
            st.session_state['selected_template'] = type_specific_default

        # Theo dõi loại template được chọn lần cuối để phát hiện thay đổi loại
        last_template_type = st.session_state.get('last_template_type', None)
        if last_template_type != selected_template_type:
            # Loại template đã đổi, reset về mặc định theo loại
            st.session_state['selected_template'] = type_specific_default
            st.session_state['last_template_type'] = selected_template_type

        # Thu thập các nhóm kích thước và chuẩn bị tab
        size_groups = []
        size_labels = []

        for size, templates in grouped_templates.items():
            if not templates:
                continue

            # Lọc template chỉ giữ những template có quy ước đặt tên đúng
            # Chỉ hiện template bắt đầu bằng static_, image_, hoặc video_
            valid_templates = []
            for template in templates:
                template_name = template.display_info.name
                if template_name.startswith(('static_', 'image_', 'video_')):
                    valid_templates.append(template)

            # Bỏ qua nếu sau lọc không còn template hợp lệ
            if not valid_templates:
                continue

            # Tách template thành hai nhóm: có preview và không có preview
            templates_with_preview = []
            templates_without_preview = []

            for template in valid_templates:
                preview_path = get_template_preview_path(template.template_path, current_lang)
                if preview_path and os.path.exists(preview_path):
                    templates_with_preview.append(template)
                else:
                    templates_without_preview.append(template)

            # Bỏ qua nhóm này nếu không có template nào
            if not templates_with_preview and not templates_without_preview:
                continue

            # Gộp: template có preview trước, sau đó đến không có preview
            all_templates = templates_with_preview + templates_without_preview

            # Lấy hướng từ template đầu tiên trong nhóm
            orientation = ORIENTATION_I18N.get(
                all_templates[0].display_info.orientation,
                all_templates[0].display_info.orientation
            )
            width = all_templates[0].display_info.width
            height = all_templates[0].display_info.height

            # Tạo nhãn tab
            tab_label = f"{orientation} {width}×{height}"
            size_labels.append(tab_label)
            size_groups.append(all_templates)

        # Tạo tab cho từng nhóm kích thước (gói trong expander)
        with st.expander(tr("template.gallery_view"), expanded=True):
            if size_groups:
                tabs = st.tabs(size_labels)

                for tab, all_templates in zip(tabs, size_groups):
                    with tab:
                        # Tạo bố cục lưới (5 cột)
                        num_cols = 5
                        cols = st.columns(num_cols)

                        for idx, template in enumerate(all_templates):
                            col_idx = idx % num_cols
                            with cols[col_idx]:
                                # Lấy đường dẫn ảnh xem trước
                                preview_path = get_template_preview_path(template.template_path, current_lang)

                                # Hiển thị ảnh xem trước hoặc placeholder
                                if preview_path and os.path.exists(preview_path):
                                    st.image(preview_path, use_container_width=True)
                                else:
                                    # Placeholder cho template không có preview (chiều cao cố định, bố cục gọn)
                                    st.markdown(
                                        f"""
                                        <div style="
                                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                                            height: 150px;
                                            display: flex;
                                            align-items: center;
                                            justify-content: center;
                                            text-align: center;
                                            border-radius: 8px;
                                            color: white;
                                            margin-bottom: 15px;
                                            padding: 10px;
                                        ">
                                            <div style="
                                                font-size: 14px; 
                                                opacity: 0.95;
                                                overflow: hidden;
                                                text-overflow: ellipsis;
                                                display: -webkit-box;
                                                -webkit-line-clamp: 5;
                                                -webkit-box-orient: vertical;
                                                word-break: break-all;
                                            ">{template.display_info.name}</div>
                                        </div>
                                        """,
                                        unsafe_allow_html=True
                                    )
                                
                                # Nút chọn (nhãn thống nhất)
                                is_selected = (st.session_state['selected_template'] == template.template_path)
                                button_label = f"{tr('template.selected')}" if is_selected else tr('template.select_button')
                                button_type = "primary" if is_selected else "secondary"

                                if st.button(
                                    button_label,
                                    key=f"template_{template.template_path}",
                                    use_container_width=True,
                                    type=button_type,
                                ):
                                    st.session_state['selected_template'] = template.template_path
                                    st.rerun()
            else:
                st.warning(tr("template.no_templates_with_preview"))

            # Hiển thị tên template đã chọn (bên trong expander, dưới các tab)
            frame_template = st.session_state['selected_template']

            # Tìm tên hiển thị của template đã chọn
            selected_template_name = None
            for size, templates in grouped_templates.items():
                for template in templates:
                    if template.template_path == frame_template:
                        selected_template_name = template.display_info.name
                        break
                if selected_template_name:
                    break

        if selected_template_name:
            st.info(f"📋 {tr('template.selected_template')}: **{selected_template_name}**")


        # Hiển thị kích thước video từ template
        from pixelle_video.utils.template_util import parse_template_size
        video_width, video_height = parse_template_size(frame_template)
        st.caption(tr("template.video_size_info", width=video_width, height=video_height))

        # Tham số template tuỳ chỉnh (cho việc sinh video)
        from pixelle_video.services.frame_html import HTMLFrameGenerator
        # Resolve đường dẫn template để hỗ trợ cả data/templates/ và templates/
        from pixelle_video.utils.template_util import resolve_template_path
        template_path_for_params = resolve_template_path(frame_template)
        generator_for_params = HTMLFrameGenerator(template_path_for_params)
        custom_params_for_video = generator_for_params.parse_template_parameters()

        # Lấy kích thước media từ template (cho việc sinh ảnh/video)
        media_width, media_height = generator_for_params.get_media_size()
        st.session_state['template_media_width'] = media_width
        st.session_state['template_media_height'] = media_height

        # Phát hiện loại media của template
        from pixelle_video.utils.template_util import get_template_type

        template_name = Path(frame_template).name
        template_media_type = get_template_type(template_name)
        template_requires_media = (template_media_type in ["image", "video"])

        # Lưu vào session state để lọc workflow
        st.session_state['template_media_type'] = template_media_type
        st.session_state['template_requires_media'] = template_requires_media

        # Tương thích ngược
        st.session_state['template_requires_image'] = (template_media_type == "image")

        custom_values_for_video = {}
        if custom_params_for_video:
            st.markdown("📝 " + tr("template.custom_parameters"))

            # Render các ô nhập tham số tuỳ chỉnh trong 2 cột
            video_custom_col1, video_custom_col2 = st.columns(2)

            param_items = list(custom_params_for_video.items())
            mid_point = (len(param_items) + 1) // 2

            # Tham số cột trái
            with video_custom_col1:
                for param_name, config in param_items[:mid_point]:
                    param_type = config['type']
                    default = config['default']
                    label = config['label']
                    
                    if param_type == 'text':
                        custom_values_for_video[param_name] = st.text_input(
                            label,
                            value=default,
                            key=f"video_custom_{param_name}"
                        )
                    elif param_type == 'number':
                        custom_values_for_video[param_name] = st.number_input(
                            label,
                            value=default,
                            key=f"video_custom_{param_name}"
                        )
                    elif param_type == 'color':
                        custom_values_for_video[param_name] = st.color_picker(
                            label,
                            value=default,
                            key=f"video_custom_{param_name}"
                        )
                    elif param_type == 'bool':
                        custom_values_for_video[param_name] = st.checkbox(
                            label,
                            value=default,
                            key=f"video_custom_{param_name}"
                        )
            
            # Tham số cột phải
            with video_custom_col2:
                for param_name, config in param_items[mid_point:]:
                    param_type = config['type']
                    default = config['default']
                    label = config['label']
                    
                    if param_type == 'text':
                        custom_values_for_video[param_name] = st.text_input(
                            label,
                            value=default,
                            key=f"video_custom_{param_name}"
                        )
                    elif param_type == 'number':
                        custom_values_for_video[param_name] = st.number_input(
                            label,
                            value=default,
                            key=f"video_custom_{param_name}"
                        )
                    elif param_type == 'color':
                        custom_values_for_video[param_name] = st.color_picker(
                            label,
                            value=default,
                            key=f"video_custom_{param_name}"
                        )
                    elif param_type == 'bool':
                        custom_values_for_video[param_name] = st.checkbox(
                            label,
                            value=default,
                            key=f"video_custom_{param_name}"
                        )
        
        # Expander xem trước template
        with st.expander(tr("template.preview_title"), expanded=False):
            col1, col2 = st.columns(2)

            with col1:
                preview_title = st.text_input(
                    tr("template.preview_param_title"),
                    value=tr("template.preview_default_title"),
                    key="preview_title"
                )
                preview_image = st.text_input(
                    tr("template.preview_param_image"),
                    value="resources/example.png",
                    help=tr("template.preview_image_help"),
                    key="preview_image"
                )

            with col2:
                preview_text = st.text_area(
                    tr("template.preview_param_text"),
                    value=tr("template.preview_default_text"),
                    height=100,
                    key="preview_text"
                )

            # Lưu ý: Kích thước được xác định tự động từ template
            from pixelle_video.utils.template_util import parse_template_size, resolve_template_path
            template_width, template_height = parse_template_size(resolve_template_path(frame_template))
            st.info(f"📐 {tr('template.size_info')}: {template_width} × {template_height}")

            # Nút xem trước
            if st.button(tr("template.preview_button"), key="btn_preview_template", use_container_width=True):
                with st.spinner(tr("template.preview_generating")):
                    try:
                        from pixelle_video.services.frame_html import HTMLFrameGenerator

                        # Sử dụng template đang chọn (kích thước được parse tự động)
                        from pixelle_video.utils.template_util import resolve_template_path
                        template_path = resolve_template_path(frame_template)
                        generator = HTMLFrameGenerator(template_path)

                        # Xây dict ext với các tham số tự động (giống FrameProcessor)
                        ext = {
                            "index": 1,  # Preview dùng index 1
                        }

                        # Thêm các tham số tuỳ chỉnh từ người dùng
                        if custom_values_for_video:
                            ext.update(custom_values_for_video)

                        # Sinh preview
                        preview_path = run_async(generator.generate_frame(
                            title=preview_title,
                            text=preview_text,
                            image=preview_image,
                            ext=ext
                        ))

                        # Hiển thị preview
                        if preview_path:
                            st.success(tr("template.preview_success"))
                            st.image(
                                preview_path,
                                caption=tr("template.preview_caption", template=frame_template),
                            )

                            # Hiển thị đường dẫn file
                            st.caption(f"📁 {preview_path}")
                        else:
                            st.error("Không thể sinh preview")

                    except Exception as e:
                        st.error(tr("template.preview_failed", error=str(e)))
                        logger.exception(e)
    
    # ====================================================================
    # Phần Sinh Media (tuỳ thuộc vào template)
    # ====================================================================
    # Kiểm tra template hiện tại có cần sinh media không
    template_media_type = st.session_state.get('template_media_type', 'image')
    template_requires_media = st.session_state.get('template_requires_media', True)

    if template_requires_media:
        # Template cần media - hiển thị phần Sinh Media
        with st.container(border=True):
            # Tiêu đề mục động theo loại template
            if template_media_type == "video":
                section_title = tr('section.video')
            else:
                section_title = tr('section.image')

            st.markdown(f"**{section_title}**")

            # 1. Chọn Workflow ComfyUI
            with st.expander(tr("help.feature_description"), expanded=False):
                st.markdown(f"**{tr('help.what')}**")
                if template_media_type == "video":
                    st.markdown(tr('style.video_workflow_what'))
                else:
                    st.markdown(tr("style.workflow_what"))
                st.markdown(f"**{tr('help.how')}**")
                if template_media_type == "video":
                    st.markdown(tr('style.video_workflow_how'))
                else:
                    st.markdown(tr("style.workflow_how"))

            # Lấy danh sách workflow khả dụng và lọc theo loại template
            all_workflows = pixelle_video.media.list_workflows()

            # Lọc workflow theo loại media của template
            if template_media_type == "video":
                # Chỉ hiển thị workflow video_
                workflows = [wf for wf in all_workflows if "video_" in wf["key"].lower()]
            else:
                # Chỉ hiển thị workflow image_ (loại trừ video_)
                workflows = [wf for wf in all_workflows if "video_" not in wf["key"].lower()]

            # Xây danh sách lựa chọn cho selectbox
            # Hiển thị: "image_flux.json - Runninghub"
            # Giá trị: "runninghub/image_flux.json"
            workflow_options = [wf["display_name"] for wf in workflows]
            workflow_keys = [wf["key"] for wf in workflows]

            # Mặc định lấy lựa chọn đầu tiên (thường là runninghub do sắp xếp)
            default_workflow_index = 0

            # Nếu người dùng đã lưu lựa chọn trong config, thử khớp với danh sách
            comfyui_config = config_manager.get_comfyui_config()
            # Chọn config theo loại template (image hoặc video)
            media_config_key = "video" if template_media_type == "video" else "image"
            saved_workflow = comfyui_config.get(media_config_key, {}).get("default_workflow", "")
            if saved_workflow and saved_workflow in workflow_keys:
                default_workflow_index = workflow_keys.index(saved_workflow)

            workflow_display = st.selectbox(
                "Workflow",
                workflow_options if workflow_options else ["Không tìm thấy workflow"],
                index=default_workflow_index,
                label_visibility="collapsed",
                key="media_workflow_select"
            )

            # Lấy key workflow thực tế (ví dụ: "runninghub/image_flux.json")
            if workflow_options:
                workflow_selected_index = workflow_options.index(workflow_display)
                workflow_key = workflow_keys[workflow_selected_index]
            else:
                workflow_key = "runninghub/image_flux.json"  # giá trị fallback

            # Kiểm tra và cảnh báo cho workflow media selfhost (tự động hiện popup nếu chưa xác nhận)
            check_and_warn_selfhost_workflow(workflow_key)

            # Lấy kích thước media từ template
            media_width = st.session_state.get('template_media_width')
            media_height = st.session_state.get('template_media_height')

            # Hiển thị thông tin kích thước media (chỉ đọc)
            if template_media_type == "video":
                size_info_text = tr('style.video_size_info', width=media_width, height=media_height)
            else:
                size_info_text = tr('style.image_size_info', width=media_width, height=media_height)
            st.info(f"📐 {size_info_text}")

            # Ô nhập tiền tố prompt
            # Lấy prompt_prefix hiện tại từ config (theo loại media)
            current_prefix = comfyui_config.get(media_config_key, {}).get("prompt_prefix", "")

            # Ô nhập tiền tố prompt (tạm thời, không lưu vào config)
            prompt_prefix = st.text_area(
                tr('style.prompt_prefix'),
                value=current_prefix,
                placeholder=tr("style.prompt_prefix_placeholder"),
                height=80,
                label_visibility="visible",
                help=tr("style.prompt_prefix_help")
            )

            # Expander xem trước media
            preview_title = tr("style.video_preview_title") if template_media_type == "video" else tr("style.preview_title")
            with st.expander(preview_title, expanded=False):
                # Ô nhập prompt thử nghiệm
                if template_media_type == "video":
                    test_prompt_label = tr("style.test_video_prompt")
                    test_prompt_value = "a dog running in the park"
                else:
                    test_prompt_label = tr("style.test_prompt")
                    test_prompt_value = "a dog"

                test_prompt = st.text_input(
                    test_prompt_label,
                    value=test_prompt_value,
                    help=tr("style.test_prompt_help"),
                    key="style_test_prompt"
                )

                # Nút xem trước
                preview_button_label = tr("style.video_preview") if template_media_type == "video" else tr("style.preview")
                if st.button(preview_button_label, key="preview_style", use_container_width=True):
                    previewing_text = tr("style.video_previewing") if template_media_type == "video" else tr("style.previewing")
                    with st.spinner(previewing_text):
                        try:
                            from pixelle_video.utils.prompt_helper import build_image_prompt

                            # Xây prompt cuối cùng kèm tiền tố
                            final_prompt = build_image_prompt(test_prompt, prompt_prefix)

                            # Sinh media xem trước (dùng kích thước và loại media người dùng chỉ định)
                            media_result = run_async(pixelle_video.media(
                                prompt=final_prompt,
                                workflow=workflow_key,
                                media_type=template_media_type,
                                width=int(media_width),
                                height=int(media_height)
                            ))
                            preview_media_path = media_result.url

                            # Hiển thị preview (hỗ trợ cả URL và đường dẫn local)
                            if preview_media_path:
                                success_text = tr("style.video_preview_success") if template_media_type == "video" else tr("style.preview_success")
                                st.success(success_text)

                                if template_media_type == "video":
                                    # Hiển thị video
                                    st.video(preview_media_path)
                                else:
                                    # Hiển thị ảnh
                                    if preview_media_path.startswith('http'):
                                        # URL - dùng trực tiếp
                                        img_html = f'<div class="preview-image"><img src="{preview_media_path}" alt="Style Preview"/></div>'
                                    else:
                                        # File local - mã hoá base64
                                        with open(preview_media_path, 'rb') as f:
                                            img_data = base64.b64encode(f.read()).decode()
                                        img_html = f'<div class="preview-image"><img src="data:image/png;base64,{img_data}" alt="Style Preview"/></div>'

                                    st.markdown(img_html, unsafe_allow_html=True)

                                # Hiển thị prompt cuối cùng đã sử dụng
                                st.info(f"**{tr('style.final_prompt_label')}**\n{final_prompt}")

                                # Hiển thị đường dẫn file
                                st.caption(f"📁 {preview_media_path}")
                            else:
                                st.error(tr("style.preview_failed_general"))
                        except Exception as e:
                            st.error(tr("style.preview_failed", error=str(e)))
                            logger.exception(e)


    else:
        # Template không cần ảnh - hiển thị thông báo đơn giản
        with st.container(border=True):
            st.markdown(f"**{tr('section.image')}**")
            st.info("ℹ️ " + tr("image.not_required"))
            st.caption(tr("image.not_required_hint"))

            # Lấy kích thước media từ template (dù không dùng, nhưng giữ tính nhất quán)
            media_width = st.session_state.get('template_media_width')
            media_height = st.session_state.get('template_media_height')

            # Đặt giá trị mặc định để dùng về sau
            workflow_key = None
            prompt_prefix = ""

    # Trả về toàn bộ tham số cấu hình style
    return {
        "tts_inference_mode": tts_mode,
        "tts_voice": selected_voice if tts_mode == "local" else None,
        "tts_speed": tts_speed if tts_mode == "local" else None,
        "tts_workflow": tts_workflow_key if tts_mode == "comfyui" else None,
        "ref_audio": str(ref_audio_path) if ref_audio_path else None,
        "frame_template": frame_template,
        "template_params": custom_values_for_video if custom_values_for_video else None,
        "media_workflow": workflow_key,
        "prompt_prefix": prompt_prefix if prompt_prefix else "",
        "media_width": media_width,
        "media_height": media_height
    }
