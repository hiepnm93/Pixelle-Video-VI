# Cài đặt

Trang này sẽ hướng dẫn bạn cài đặt Pixelle-Video.

---

## Yêu cầu hệ thống

### Bắt buộc

- **Python**: 3.10 trở lên
- **Hệ điều hành**: Windows, macOS hoặc Linux
- **Trình quản lý gói**: uv (khuyến nghị) hoặc pip

### Tuỳ chọn

- **GPU**: GPU NVIDIA với 6GB VRAM trở lên, khuyến nghị cho ComfyUI cục bộ
- **Mạng**: Kết nối Internet ổn định cho LLM API và dịch vụ sinh ảnh

---

## 🪟 Bản Windows All-in-One (Khuyến nghị cho người dùng Windows)

**Không cần cài Python, uv hay ffmpeg — mở ra là dùng được luôn!**

### Tải và cài đặt

1. Truy cập [GitHub Releases](https://github.com/AIDC-AI/Pixelle-Video/releases/latest) để tải bản mới nhất
2. Tải bản Windows All-in-One mới nhất và giải nén vào thư mục bất kỳ
3. Nháy đúp vào `start.bat` để mở giao diện Web
4. Trình duyệt sẽ tự động mở `http://localhost:8501`

!!! success "Cài đặt hoàn tất!"
    Bản đóng gói đã bao gồm toàn bộ phụ thuộc, không cần cài đặt môi trường thủ công. Lần đầu chỉ cần cấu hình API key trong "⚙️ Cấu hình hệ thống" là có thể bắt đầu.

!!! tip "Bước tiếp theo"
    Sau khi cài đặt, hãy xem [Hướng dẫn cấu hình](configuration.md) để thiết lập LLM và dịch vụ sinh ảnh, rồi xem [Bắt đầu nhanh](quick-start.md) để tạo video đầu tiên.

---

## Cài từ mã nguồn (cho macOS / Linux hoặc người cần tuỳ biến)

### Bước 1: Clone repository

```bash
git clone https://github.com/AIDC-AI/Pixelle-Video.git
cd Pixelle-Video
```

### Bước 2: Cài phụ thuộc

!!! tip "Khuyến nghị: Dùng uv"
    Dự án này dùng `uv` làm trình quản lý gói, nhanh và đáng tin cậy hơn pip truyền thống.

#### Dùng uv (Khuyến nghị)

```bash
# Cài uv nếu chưa có
curl -LsSf https://astral.sh/uv/install.sh | sh

# Cài phụ thuộc dự án (uv tự tạo virtual environment)
uv sync
```

#### Dùng pip

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Cài phụ thuộc
pip install -e .
```

---

## Kiểm tra cài đặt

Chạy lệnh sau để kiểm tra cài đặt:

```bash
# Dùng uv
uv run streamlit run web/app.py

# Hoặc dùng pip (kích hoạt virtual environment trước)
streamlit run web/app.py
```

Trình duyệt sẽ tự động mở `http://localhost:8501` và hiển thị giao diện web Pixelle-Video.

!!! success "Cài đặt thành công!"
    Nếu bạn nhìn thấy giao diện web, cài đặt đã thành công! Tiếp theo, hãy xem [Hướng dẫn cấu hình](configuration.md) để thiết lập các dịch vụ.

---

## Tuỳ chọn: Cài ComfyUI (triển khai cục bộ)

Nếu bạn muốn chạy sinh ảnh cục bộ, bạn cần cài ComfyUI:

### Cài đặt nhanh

```bash
# Clone ComfyUI
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI

# Cài phụ thuộc
pip install -r requirements.txt
```

### Khởi động ComfyUI

```bash
python main.py
```

ComfyUI mặc định chạy tại `http://127.0.0.1:8188`.

!!! info "Model của ComfyUI"
    ComfyUI cần tải các file model về để hoạt động. Vui lòng tham khảo [tài liệu ComfyUI](https://github.com/comfyanonymous/ComfyUI) để biết cách tải và cấu hình model.

---

## Bước tiếp theo

- [Cấu hình](configuration.md) — Cấu hình LLM và dịch vụ sinh ảnh
- [Bắt đầu nhanh](quick-start.md) — Tạo video đầu tiên của bạn
