# 🙋‍♀️ Câu hỏi thường gặp (FAQ) Pixelle-Video

### Làm sao để tích hợp workflow tự phát triển ở local?

Nếu bạn muốn tích hợp các workflow ComfyUI tự phát triển, vui lòng tuân theo các quy ước sau:

1.  **Chạy thử ở local trước**: Đảm bảo workflow chạy bình thường trong ComfyUI ở máy của bạn.
2.  **Gắn (bind) tham số**: Tìm node Text (CLIP Text Encode hoặc node nhập văn bản tương tự) cần được chương trình truyền prompt động vào.
    -   Chỉnh sửa **Title** của node đó.
    -   Đổi title thành `$prompt.text!` hoặc `$prompt.value!` (tuỳ vào kiểu input mà node chấp nhận).
     <img src="https://github.com/user-attachments/assets/ddb1962c-9272-486f-84ab-8019c3fb5bf4" width="600" alt="Ví dụ gắn tham số" />

    -   *Ví dụ tham khảo: xem cách chỉnh sửa của các file JSON hiện có trong thư mục `workflows/selfhost/`.*
3.  **Định dạng xuất**: Xuất workflow đã chỉnh sửa ở **định dạng API** (Save (API Format)).
4.  **Đặt tên file**: Đặt file JSON đã xuất vào thư mục `workflows/` và tuân thủ các tiền tố tên sau:
    -   **Workflow tạo ảnh**: tiền tố bắt buộc là `image_` (ví dụ `image_my_style.json`)
    -   **Workflow tạo video**: tiền tố bắt buộc là `video_`
    -   **Workflow TTS**: tiền tố bắt buộc là `tts_`

### Làm sao để debug workflow RunningHub ở local?

Nếu bạn muốn test ở local các workflow vốn được dùng trên cloud RunningHub:

1.  **Lấy ID**: Mở file workflow RunningHub và tìm ID.
2.  **Tải workflow**: Dán ID vào sau URL của RunningHub (ví dụ: https://www.runninghub.cn/workflow/1983513964837543938) để vào trang workflow.
  <img src="https://github.com/user-attachments/assets/e5330b3a-5475-44f2-81e4-057d33fdf71b" width="600" alt="Ví dụ gắn tham số" />


3.  **Tải về máy**: Trong workbench, tải workflow xuống dưới dạng file JSON.
4.  **Test ở local**: Kéo file đã tải vào canvas ComfyUI ở máy của bạn để test và debug.

### Các lỗi thường gặp và cách khắc phục

#### 1. Lỗi TTS (Text-to-Speech)
-   **Nguyên nhân**: Edge-TTS mặc định gọi tới interface miễn phí của Microsoft, có thể bị fail thường xuyên do mạng không ổn định.
-   **Giải pháp**:
    -   Kiểm tra kết nối mạng.
    -   Khuyến nghị chuyển sang dùng workflow **ComfyUI TTS** (chọn workflow có tiền tố `tts_`) để có độ ổn định cao hơn.

#### 2. Lỗi LLM (Large Language Model)
-   **Các bước kiểm tra**:
    1.  Kiểm tra **Base URL** đã đúng chưa (đảm bảo không có khoảng trắng thừa hoặc hậu tố sai).
    2.  Kiểm tra **API Key** còn hợp lệ và còn số dư hay không.
    3.  Kiểm tra **Model Name** đã viết đúng chính tả chưa.
    -   *Mẹo: Vui lòng tham khảo tài liệu API chính thức của nhà cung cấp model bạn đang dùng (ví dụ OpenAI, DeepSeek, Alibaba Cloud, v.v.) để có cấu hình chính xác.*

#### 3. Thông báo lỗi "Could not find a Chrome executable..."
-   **Nguyên nhân**: Hệ thống máy tính của bạn thiếu nhân trình duyệt Chrome, khiến các tính năng phụ thuộc vào trình duyệt không chạy được.
-   **Giải pháp**: Vui lòng tải và cài đặt trình duyệt Google Chrome.

### Video đã tạo được lưu ở đâu?

Tất cả video đã tạo sẽ được tự động lưu vào thư mục `output/` trong thư mục dự án. Sau khi hoàn tất, giao diện sẽ hiển thị thời lượng video, kích thước file, số phân cảnh và link tải xuống.

### Tài nguyên cộng đồng

-   **Repository GitHub**: https://github.com/AIDC-AI/Pixelle-Video
-   **Báo lỗi**: Gửi bug hoặc đề xuất tính năng qua GitHub Issues.
-   **Hỗ trợ cộng đồng**: Tham gia các nhóm thảo luận để được trợ giúp và chia sẻ kinh nghiệm.
-   **Đóng góp**: Dự án phát hành theo giấy phép MIT, hoan nghênh mọi đóng góp.

💡 **Mẹo**: Nếu bạn không tìm thấy câu trả lời cần thiết trong FAQ này, vui lòng tạo issue trên GitHub hoặc tham gia thảo luận cộng đồng. Chúng tôi sẽ tiếp tục cập nhật FAQ này dựa trên phản hồi của người dùng!
