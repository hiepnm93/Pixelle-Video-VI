<h1 align="center">🎬 Pixelle-Video — Engine tạo video ngắn hoàn toàn tự động bằng AI</h1>

<p align="center"><b>Tiếng Việt</b> | <a href="README_EN.md">English</a> | <a href="README_ZH.md">中文</a></p>

<p align="center">
  <a href="https://www.youtube.com/watch?v=uUkx-lRxLjc" target="_blank"><img src="https://img.shields.io/badge/🎥 Video%20hướng%20dẫn-EA4C89" alt="Video hướng dẫn"></a>
  <a href="https://github.com/hiepnm93/Pixelle-Video-VI/releases" target="_blank"><img src="https://img.shields.io/badge/📦 Windows-50C878" alt="Windows Package"></a>
  <a href="https://aidc-ai.github.io/Pixelle-Video" target="_blank"><img src="https://img.shields.io/badge/📘 Tài%20liệu-4A90E2" alt="Tài liệu"></a>
  <a href="https://github.com/hiepnm93/Pixelle-Video-VI/stargazers"><img src="https://img.shields.io/github/stars/hiepnm93/Pixelle-Video-VI.svg" alt="Stargazers"></a>
  <a href="https://github.com/hiepnm93/Pixelle-Video-VI/issues"><img src="https://img.shields.io/github/issues/hiepnm93/Pixelle-Video-VI.svg" alt="Issues"></a>
  <a href="https://github.com/hiepnm93/Pixelle-Video-VI/network/members"><img src="https://img.shields.io/github/forks/hiepnm93/Pixelle-Video-VI.svg" alt="Forks"></a>
  <a href="https://github.com/hiepnm93/Pixelle-Video-VI/blob/main/LICENSE"><img src="https://img.shields.io/github/license/hiepnm93/Pixelle-Video-VI.svg" alt="License"></a>
</p>

https://github.com/user-attachments/assets/a42e7457-fcc8-40da-83fc-784c45a8b95d

Chỉ cần nhập một **chủ đề**, Pixelle-Video sẽ tự động:
- ✍️ Viết kịch bản video
- 🎨 Tạo hình ảnh / video bằng AI
- 🗣️ Tổng hợp giọng đọc thuyết minh
- 🎵 Thêm nhạc nền
- 🎬 Tạo video chỉ với một cú nhấp chuột

**Không cần kiến thức chuyên môn, không cần kinh nghiệm dựng phim** — Tạo video đơn giản như gõ một câu chữ!


## 🖥️ Xem trước giao diện Web

![Giao diện Web UI](resources/webui_en.png)


## 📋 Cập nhật gần đây

- ✅ **2026-01-26**: Thêm pipeline Motion Transfer — tải lên một video tham chiếu và một ảnh để chuyển động.
- ✅ **2026-01-14**: Thêm pipeline "Người ảo (Digital Human)" và "Ảnh thành Video", hỗ trợ TTS đa ngôn ngữ
- ✅ **2026-01-06**: Hỗ trợ máy RunningHub 48G VRAM
- ✅ **2025-12-28**: Có thể cấu hình giới hạn concurrency của RunningHub, cải tiến xử lý dữ liệu có cấu trúc trả về từ LLM
- ✅ **2025-12-17**: Thêm cấu hình ComfyUI API Key, hỗ trợ model Nano Banana, tham số tuỳ chỉnh cho API template
- ✅ **2025-12-10**: Tích hợp FAQ ngay trong sidebar, cố định phiên bản edge-tts để khắc phục lỗi TTS không ổn định
- ✅ **2025-12-08**: Hỗ trợ nhiều chế độ tách kịch bản (đoạn / dòng / câu), cải tiến chọn template với xem trước trực tiếp
- ✅ **2025-12-06**: Sửa lỗi xử lý đường dẫn URL của API tạo video, tương thích đa nền tảng
- ✅ **2025-12-05**: Thêm bản tải Windows All-in-One, tối ưu workflow phân tích ảnh và video
- ✅ **2025-12-04**: Tính năng mới "Custom Media" — tải ảnh / video của bạn lên, AI tự phân tích và tạo kịch bản
- ✅ **2025-11-18**: Xử lý song song cho RunningHub, thêm trang lịch sử, hỗ trợ tạo nhiều task video cùng lúc


## ✨ Tính năng nổi bật

- ✅ **Tạo video hoàn toàn tự động** — Nhập một chủ đề, hệ thống tự sinh ra video hoàn chỉnh
- ✅ **Viết kịch bản thông minh bằng AI** — Tự động sáng tác lời thuyết minh dựa trên chủ đề, không cần tự viết kịch bản
- ✅ **Sinh ảnh bằng AI** — Mỗi câu thuyết minh đi kèm một hình minh hoạ AI đẹp mắt
- ✅ **Sinh video bằng AI** — Hỗ trợ các model sinh video AI (như WAN 2.1) để tạo nội dung video động
- ✅ **Sinh giọng nói bằng AI** — Hỗ trợ Edge-TTS, Index-TTS và nhiều giải pháp TTS phổ biến khác
- ✅ **Nhạc nền (BGM)** — Hỗ trợ thêm nhạc nền, làm video giàu cảm xúc hơn
- ✅ **Phong cách hình ảnh** — Nhiều template để chọn, tạo phong cách video độc đáo
- ✅ **Kích thước linh hoạt** — Hỗ trợ video dọc, ngang và nhiều tỉ lệ khác
- ✅ **Đa dạng model AI** — Hỗ trợ GPT, Qwen, DeepSeek, Ollama và nhiều model khác
- ✅ **Kết hợp năng lực nguyên tử linh hoạt** — Dựa trên kiến trúc ComfyUI, có thể dùng workflow có sẵn hoặc tuỳ biến mọi năng lực (ví dụ thay model sinh ảnh bằng FLUX, thay TTS bằng ChatTTS, v.v.)


## 📊 Pipeline tạo video

Pixelle-Video có thiết kế module hoá, toàn bộ quy trình tạo video rõ ràng và súc tích:

![Quy trình tạo video](resources/flow_en.png)

Từ văn bản đầu vào đến video đầu ra cuối cùng, toàn bộ quy trình rất rõ ràng và đơn giản: **Sinh kịch bản → Lập kế hoạch hình ảnh → Xử lý từng khung hình → Ghép video**

Mỗi bước đều hỗ trợ tuỳ biến linh hoạt, cho phép bạn chọn các model AI, engine âm thanh, phong cách hình ảnh khác nhau để đáp ứng nhu cầu sáng tạo cá nhân hoá.


## 🎬 Ví dụ video

Dưới đây là các video thực tế tạo ra bằng Pixelle-Video, minh hoạ hiệu quả trên các chủ đề và phong cách khác nhau:

### 📱 Trình diễn module mở rộng

<table>
<tr>
<td width="33%">
<h3>👤 Người ảo (AI Digital Avatar)</h3>
<video src="https://github.com/user-attachments/assets/7c122563-c2e0-4dcd-a73c-25ba1d4fa2dd" controls width="100%"></video>
<p align="center"><b>Người ảo nói tiếng Hàn</b></p>
</td>
<td width="33%">
<h3>🖼️ Ảnh thành Video</h3>
<video src="https://github.com/user-attachments/assets/5b4eef17-07d0-4bde-9748-2ed68cc9888e" controls width="100%"></video>
<p align="center"><b>Video hoạt hình</b></p>
</td>
<td width="33%">
<h3>💃 Motion Transfer</h3>
<video src="https://github.com/user-attachments/assets/7b1240bc-e965-434c-b343-118ec4793d4f" controls width="100%"></video>
<p align="center"><b>Mèo con nhảy múa</b></p>
</td>
</tr>
</table>

### 📱 Trình diễn video dọc

<table>
<tr>
<td width="33%">
<h3>🌄 Phim tài liệu & đời sống – Template mặc định</h3>
<video src="https://github.com/user-attachments/assets/e6716c1d-78de-453d-84c2-10873c8c595f" controls width="100%"></video>
<p align="center"><b>Cảnh sắc trên đường đi</b></p>
</td>
<td width="33%">
<h3>🔍 Giải mã văn hoá – Template mặc định</h3>
<video src="https://github.com/user-attachments/assets/f5de75f6-135a-4ab4-9f5f-079f649764d5" controls width="100%"></video>
<p align="center"><b>Lai lịch ông già Noel</b></p>
</td>
<td width="33%">
<h3>🔭 Khoa học khám phá – Template mặc định</h3>
<video src="https://github.com/user-attachments/assets/ceb8b0df-8331-4e1f-88e7-db5b295a1c1d" controls width="100%"></video>
<p align="center"><b>Vì sao chưa tìm thấy nền văn minh ngoài Trái Đất?</b></p>
</td>
</tr>
<tr>
<td width="33%">
<h3>🌱 Phát triển bản thân – Giọng nhân bản</h3>
<video src="https://github.com/user-attachments/assets/1bad9a49-df83-4905-9cc8-9a7640e9c7d8" controls width="100%"></video>
<p align="center"><b>Cách nâng cấp bản thân</b></p>
</td>
<td width="33%">
<h3>🧠 Tư duy chuyên sâu – Template mặc định</h3>
<video src="https://github.com/user-attachments/assets/663b705a-2aea-44bc-b266-4bb27aa255a8" controls width="100%"></video>
<p align="center"><b>Hiểu về Phản mong manh (Antifragility)</b></p>
</td>
<td width="33%">
<h3>🏯 Lịch sử & văn hoá – Khung tĩnh</h3>
<video src="https://github.com/user-attachments/assets/56e0a018-fa99-47eb-a97f-fc2fa8915724" controls width="100%"></video>
<p align="center"><b>Tư Trị Thông Giám</b></p>
</td>
</tr>
<tr>
<td width="33%">
<h3>☀️ Kể chuyện cảm xúc – Giọng nhân bản</h3>
<video src="https://github.com/user-attachments/assets/4687df95-dd21-4a7b-b01e-f33a7b646644" controls width="100%"></video>
<p align="center"><b>Nắng mùa đông</b></p>
</td>
<td width="33%">
<h3>📜 Phóng tác tiểu thuyết – Kịch bản tuỳ chỉnh</h3>
<video src="https://github.com/user-attachments/assets/d354465e-3fa8-40b4-93e9-61ad75ef0697" controls width="100%"></video>
<p align="center"><b>Đấu Phá Thương Khung</b></p>
</td>
<td width="33%">
<h3>🧬 Giải thích kiến thức – Sinh ảnh Qwen</h3>
<video src="https://github.com/user-attachments/assets/8ac21768-41ce-4d41-acdd-e3dd3eb9725a" controls width="100%"></video>
<p align="center"><b>Bí quyết dưỡng sinh thiết yếu</b></p>
</td>
</tr>
</table>

### 🖥️ Trình diễn video ngang

<table>
<tr>
<td width="50%">
<h3>💰 Kiếm tiền tay trái — Template phim ảnh</h3>
<video src="https://github.com/user-attachments/assets/c9209d4e-73a6-4b82-aaad-cf102248c9e2" controls width="100%"></video>
<p align="center"><b>Kiếm tiền tay trái</b></p>
</td>
<td width="50%">
<h3>🏛️ Bình luận lịch sử — Template tuỳ chỉnh</h3>
<video src="https://github.com/user-attachments/assets/a767c452-d5f1-4cff-bb34-b80fff0d4c3e" controls width="100%"></video>
<p align="center"><b>Suy ngẫm từ Tư Trị Thông Giám</b></p>
</td>
</tr>
</table>

> 💡 **Mẹo**: Toàn bộ video trên đều được AI tạo hoàn toàn tự động chỉ từ một từ khoá chủ đề, không cần bất kỳ kinh nghiệm dựng phim nào!

<div id="tutorial-start" />

## 🚀 Bắt đầu nhanh

### 🪟 Bản Windows All-in-One (Khuyến nghị cho người dùng Windows)

**Không cần cài Python, uv hay ffmpeg — mở ra là dùng được luôn!**

👉 **[Tải bản Windows All-in-One](https://github.com/AIDC-AI/Pixelle-Video/releases/latest)**

1. Tải bản Windows All-in-One mới nhất và giải nén
2. Nháy đúp vào `start.bat` để mở giao diện Web
3. Trình duyệt sẽ tự động mở http://localhost:8501
4. Cấu hình LLM API và dịch vụ sinh ảnh trong "⚙️ Cấu hình hệ thống"
5. Bắt đầu tạo video!

> 💡 **Mẹo**: Bản đóng gói đã bao gồm toàn bộ phụ thuộc, không cần cài đặt môi trường thủ công. Lần đầu chỉ cần cấu hình API key.


### Cài đặt từ mã nguồn (Dành cho macOS / Linux hoặc người dùng cần tuỳ biến)

#### Yêu cầu trước khi cài

Trước khi bắt đầu, bạn cần cài trình quản lý gói Python `uv` và công cụ xử lý video `ffmpeg`:

##### Cài uv

Hãy truy cập tài liệu chính thức của uv để xem cách cài cho hệ điều hành của bạn:  
👉 **[Hướng dẫn cài uv](https://docs.astral.sh/uv/getting-started/installation/)**

Sau khi cài xong, chạy `uv --version` trong terminal để kiểm tra cài đặt thành công.

##### Cài ffmpeg

**macOS**
```bash
brew install ffmpeg
```

**Ubuntu / Debian**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows**
- Đường dẫn tải: https://ffmpeg.org/download.html
- Sau khi tải, giải nén và thêm thư mục `bin` vào biến môi trường PATH của hệ thống

Sau khi cài, chạy `ffmpeg -version` trong terminal để kiểm tra cài đặt thành công.


#### Bước 1: Clone dự án

```bash
git clone https://github.com/hiepnm93/Pixelle-Video-VI.git
cd Pixelle-Video-VI
```

#### Bước 2: Khởi chạy giao diện Web

```bash
# Chạy với uv (khuyến nghị, tự động cài phụ thuộc)
uv run streamlit run web/app.py
```

Trình duyệt sẽ tự động mở http://localhost:8501

#### Bước 3: Cấu hình trong giao diện Web

Lần đầu sử dụng, mở rộng panel "⚙️ Cấu hình hệ thống" và điền:
- **Cấu hình LLM**: Chọn model AI (như Qwen, GPT, …) và nhập API Key
- **Cấu hình hình ảnh**: Nếu cần sinh ảnh, hãy cấu hình địa chỉ ComfyUI hoặc API Key của RunningHub

Sau khi cấu hình xong, nhấn "Lưu cấu hình" và bạn có thể bắt đầu tạo video!

<div id="tutorial-end" />

## 💻 Hướng dẫn sử dụng

Sau khi mở giao diện Web, bạn sẽ thấy bố cục ba cột. Dưới đây là giải thích chi tiết từng phần:


### ⚙️ Cấu hình hệ thống (Bắt buộc khi dùng lần đầu)

Lần đầu sử dụng cần cấu hình. Nhấn để mở rộng panel "⚙️ Cấu hình hệ thống":

#### 1. Cấu hình LLM (Mô hình ngôn ngữ lớn)
Dùng để sinh kịch bản video.

**Chọn nhanh từ preset**  
- Chọn model preset từ menu (Qwen, GPT-4o, DeepSeek, …)
- Sau khi chọn, base_url và model sẽ được điền tự động
- Nhấn liên kết "🔑 Lấy API Key" để đăng ký và lấy key

**Cấu hình thủ công**  
- API Key: Nhập key của bạn
- Base URL: Địa chỉ API
- Model: Tên model

#### 2. Cấu hình hình ảnh
Dùng để sinh hình minh hoạ cho video.

**Triển khai cục bộ (Khuyến nghị)**  
- ComfyUI URL: Địa chỉ dịch vụ ComfyUI cục bộ (mặc định http://127.0.0.1:8188)
- Nhấn "Test Connection" để xác nhận dịch vụ khả dụng

**Triển khai trên cloud**  
- RunningHub API Key: Key dịch vụ sinh ảnh trên cloud

Sau khi cấu hình, nhấn "Lưu cấu hình".


### 📝 Nhập nội dung (Cột trái)

#### Chế độ sinh
- **Sinh nội dung bằng AI**: Nhập chủ đề, AI tự sáng tác kịch bản
  - Phù hợp khi: Muốn nhanh chóng có video, để AI viết kịch bản
  - Ví dụ: "Tại sao nên rèn luyện thói quen đọc sách"
- **Kịch bản cố định**: Nhập trực tiếp kịch bản hoàn chỉnh, bỏ qua phần sáng tác AI
  - Phù hợp khi: Đã có sẵn kịch bản, chỉ muốn sinh video

#### Nhạc nền (BGM)
- **Không nhạc nền**: Chỉ có giọng đọc thuần
- **Nhạc có sẵn**: Chọn nhạc nền preset (như default.mp3)
- **Nhạc tuỳ chỉnh**: Đặt file nhạc của bạn (MP3 / WAV, …) vào thư mục `bgm/`
- Nhấn "Nghe thử BGM" để nghe trước nhạc


### 🎤 Cài đặt giọng đọc (Cột giữa)

#### Workflow TTS
- Chọn workflow TTS từ menu (hỗ trợ Edge-TTS, Index-TTS, …)
- Hệ thống sẽ tự động quét workflow TTS trong thư mục `workflows/`
- Nếu bạn rành ComfyUI, có thể tự thiết kế workflow TTS

#### Audio tham chiếu (Tuỳ chọn)
- Tải lên file audio tham chiếu để nhân bản giọng (hỗ trợ MP3 / WAV / FLAC, …)
- Phù hợp với workflow TTS hỗ trợ nhân bản giọng (như Index-TTS)
- Có thể nghe trực tiếp sau khi tải lên

#### Chức năng nghe thử
- Nhập đoạn văn thử, nhấn "Nghe thử giọng" để kiểm tra hiệu quả
- Hỗ trợ dùng audio tham chiếu khi nghe thử


### 🎨 Cài đặt hình ảnh (Cột giữa)

#### Sinh hình ảnh
Quyết định AI sinh ảnh theo phong cách nào.

**Workflow ComfyUI**  
- Chọn workflow sinh ảnh từ menu
- Hỗ trợ workflow cục bộ (selfhost) và cloud (RunningHub)
- Mặc định dùng `image_flux.json`
- Nếu rành ComfyUI, bạn có thể đặt workflow của mình vào thư mục `workflows/`

**Kích thước ảnh**  
- Đặt chiều rộng và chiều cao của ảnh sinh ra (đơn vị: pixel)
- Mặc định 1024x1024, có thể chỉnh theo nhu cầu
- Lưu ý: Mỗi model có giới hạn kích thước khác nhau

**Tiền tố prompt**  
- Điều khiển phong cách tổng thể của ảnh (cần viết bằng tiếng Anh)
- Ví dụ: Minimalist black-and-white matchstick figure style illustration, clean lines, simple sketch style
- Nhấn "Nghe thử phong cách" để kiểm tra hiệu quả

#### Template video
Quyết định bố cục và thiết kế của video.

**Quy ước đặt tên template**  
- `static_*.html`: Template tĩnh (không có media do AI tạo, chỉ phong cách chữ)
- `image_*.html`: Template ảnh (dùng ảnh AI sinh làm nền)
- `video_*.html`: Template video (dùng video AI sinh làm nền)

**Cách dùng**  
- Chọn template từ menu, hiển thị nhóm theo kích thước (dọc / ngang / vuông)
- Nhấn "Xem trước template" để thử với tham số tuỳ chỉnh
- Nếu rành HTML, bạn có thể tự tạo template trong thư mục `templates/`
- 🔗 [Xem toàn bộ template preview](https://aidc-ai.github.io/Pixelle-Video/user-guide/templates/#built-in-template-preview)


### 🎬 Tạo video (Cột phải)

#### Nút Tạo video
- Sau khi cấu hình toàn bộ, nhấn "🎬 Tạo video"
- Hiển thị tiến độ thời gian thực (sinh kịch bản → sinh ảnh → tổng hợp giọng → ghép video)
- Tự động hiển thị video xem trước sau khi xong

#### Hiển thị tiến độ
- Hiển thị bước hiện tại theo thời gian thực
- Ví dụ: "Khung 3/5 — Đang sinh ảnh"

#### Xem trước video
- Tự động phát sau khi sinh xong
- Hiển thị thời lượng, dung lượng, số khung hình, …
- File video được lưu trong thư mục `output/`


### ❓ Câu hỏi thường gặp

**Q: Lần đầu tạo video mất bao lâu?**  
A: Thời gian phụ thuộc vào số khung hình, tốc độ mạng và tốc độ inference của AI, thường hoàn tất trong vài phút.

**Q: Nếu video chưa ưng ý thì sao?**  
A: Bạn có thể thử:
1. Đổi model LLM (mỗi model có phong cách kịch bản khác nhau)
2. Chỉnh kích thước ảnh và tiền tố prompt (đổi phong cách hình)
3. Đổi workflow TTS hoặc tải audio tham chiếu (đổi giọng đọc)
4. Thử template và kích thước video khác

**Q: Chi phí thì sao?**  
A: **Dự án hỗ trợ chạy hoàn toàn miễn phí!**

- **Phương án miễn phí hoàn toàn**: LLM dùng Ollama (local) + ComfyUI cục bộ = 0 chi phí
- **Phương án khuyến nghị**: LLM dùng Qwen (chi phí cực thấp, hiệu năng / giá rất tốt) + ComfyUI cục bộ
- **Phương án cloud**: LLM dùng OpenAI + Sinh ảnh dùng RunningHub (chi phí cao hơn nhưng không cần môi trường cục bộ)

**Gợi ý lựa chọn**: Nếu bạn có GPU cục bộ, hãy dùng phương án miễn phí; ngược lại nên dùng Qwen (rẻ và hiệu quả)


## 🤝 Các dự án tham khảo

Pixelle-Video lấy cảm hứng thiết kế từ các dự án mã nguồn mở xuất sắc sau:

- [Pixelle-MCP](https://github.com/AIDC-AI/Pixelle-MCP) — Server MCP cho ComfyUI, cho phép trợ lý AI gọi trực tiếp ComfyUI
- [MoneyPrinterTurbo](https://github.com/harry0703/MoneyPrinterTurbo) — Công cụ tạo video xuất sắc
- [NarratoAI](https://github.com/linyqh/NarratoAI) — Công cụ tự động bình luận phim
- [MoneyPrinterPlus](https://github.com/ddean2009/MoneyPrinterPlus) — Nền tảng sáng tạo video
- [ComfyKit](https://github.com/puke3615/ComfyKit) — Thư viện đóng gói workflow ComfyUI

Cảm ơn tinh thần mã nguồn mở của các dự án trên! 🙏


## 💬 Cộng đồng

Quét mã QR dưới đây để tham gia cộng đồng, nhận cập nhật mới và hỗ trợ kỹ thuật:

| Cộng đồng Discord | Nhóm WeChat |
| ---- | ---- |
| <img src="resources/discord.png" alt="Cộng đồng Discord" width="250" /> | <img src="resources/wechat.png" alt="Nhóm WeChat" width="250" /> |


## 📢 Phản hồi và hỗ trợ

- 🐛 **Gặp vấn đề**: Tạo [Issue](https://github.com/hiepnm93/Pixelle-Video-VI/issues)
- 💡 **Đề xuất tính năng**: Tạo [Feature Request](https://github.com/hiepnm93/Pixelle-Video-VI/issues)
- ⭐ **Tặng Star**: Nếu dự án giúp ích cho bạn, hãy tặng một Star để ủng hộ!


## 📝 Giấy phép

Dự án được phát hành theo Apache License 2.0. Xem chi tiết tại file [LICENSE](LICENSE).


## 🌐 Bản dịch tiếng Việt

Bản tiếng Việt này được dịch và duy trì bởi [@hiepnm93](https://github.com/hiepnm93) từ dự án gốc [AIDC-AI/Pixelle-Video](https://github.com/AIDC-AI/Pixelle-Video). Mọi đóng góp về bản dịch đều được hoan nghênh!


## ⭐ Lịch sử Star

[![Star History Chart](https://api.star-history.com/svg?repos=AIDC-AI/Pixelle-Video&type=Date)](https://star-history.com/#AIDC-AI/Pixelle-Video&Date)
