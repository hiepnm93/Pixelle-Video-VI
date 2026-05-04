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
Ứng dụng FastAPI của Pixelle-Video

Ứng dụng FastAPI chính với tất cả router và middleware.

Chạy script này để khởi động FastAPI server:
    uv run python api/app.py

Hoặc với cấu hình tuỳ chỉnh:
    uv run python api/app.py --host 0.0.0.0 --port 8080 --reload
"""

import sys
from pathlib import Path

# Thêm thư mục gốc của dự án vào sys.path để import module
# Điều này đảm bảo import hoạt động đúng cả trong môi trường phát triển và đóng gói
_script_dir = Path(__file__).resolve().parent
_project_root = _script_dir.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import argparse
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from api.config import api_config
from api.tasks import task_manager
from api.dependencies import shutdown_pixelle_video

# Import các router
from api.routers import (
    health_router,
    llm_router,
    tts_router,
    image_router,
    content_router,
    video_router,
    tasks_router,
    files_router,
    resources_router,
    frame_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Trình quản lý vòng đời của ứng dụng

    Xử lý các sự kiện khởi động và tắt.
    """
    # Khởi động
    logger.info("🚀 Đang khởi động Pixelle-Video API...")
    await task_manager.start()
    logger.info("✅ Pixelle-Video API đã khởi động thành công\n")

    yield

    # Tắt
    logger.info("🛑 Đang tắt Pixelle-Video API...")
    await task_manager.stop()
    await shutdown_pixelle_video()
    logger.info("✅ Pixelle-Video API đã tắt hoàn tất")


# Tạo ứng dụng FastAPI
app = FastAPI(
    title="Pixelle-Video API",
    description="""
    ## Pixelle-Video - API nền tảng tạo video bằng AI

    ### Tính năng
    - 🤖 **LLM**: Tích hợp mô hình ngôn ngữ lớn
    - 🔊 **TTS**: Tổng hợp giọng nói từ văn bản
    - 🎨 **Image**: Tạo ảnh bằng AI
    - 📝 **Content**: Tạo nội dung tự động
    - 🎬 **Video**: Tạo video đầu cuối

    ### Chế độ tạo video
    - **Sync**: `/api/video/generate/sync` - Cho video nhỏ (< 30s)
    - **Async**: `/api/video/generate/async` - Cho video lớn, có theo dõi task

    ### Bắt đầu
    1. Kiểm tra trạng thái: `GET /health`
    2. Tạo lời thoại: `POST /api/content/narration`
    3. Tạo video: `POST /api/video/generate/sync` hoặc `/async`
    4. Theo dõi tiến trình task: `GET /api/tasks/{task_id}`
    """,
    version="0.1.0",
    docs_url=api_config.docs_url,
    redoc_url=api_config.redoc_url,
    openapi_url=api_config.openapi_url,
    lifespan=lifespan,
)

# Thêm middleware CORS
if api_config.cors_enabled:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=api_config.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    logger.info(f"Đã bật CORS cho các origin: {api_config.cors_origins}")

# Đăng ký các router
# Health check (không có prefix)
app.include_router(health_router)

# Các router API (có prefix /api)
app.include_router(llm_router, prefix=api_config.api_prefix)
app.include_router(tts_router, prefix=api_config.api_prefix)
app.include_router(image_router, prefix=api_config.api_prefix)
app.include_router(content_router, prefix=api_config.api_prefix)
app.include_router(video_router, prefix=api_config.api_prefix)
app.include_router(tasks_router, prefix=api_config.api_prefix)
app.include_router(files_router, prefix=api_config.api_prefix)
app.include_router(resources_router, prefix=api_config.api_prefix)
app.include_router(frame_router, prefix=api_config.api_prefix)


@app.get("/")
async def root():
    """Endpoint gốc trả về thông tin API"""
    return {
        "service": "Pixelle-Video API",
        "version": "0.1.0",
        "docs": api_config.docs_url,
        "health": "/health",
        "api": {
            "llm": f"{api_config.api_prefix}/llm",
            "tts": f"{api_config.api_prefix}/tts",
            "image": f"{api_config.api_prefix}/image",
            "content": f"{api_config.api_prefix}/content",
            "video": f"{api_config.api_prefix}/video",
            "tasks": f"{api_config.api_prefix}/tasks",
            "files": f"{api_config.api_prefix}/files",
            "resources": f"{api_config.api_prefix}/resources",
            "frame": f"{api_config.api_prefix}/frame",
        }
    }


if __name__ == "__main__":
    import uvicorn
    
    # Phân tích tham số dòng lệnh
    parser = argparse.ArgumentParser(description="Khởi động Pixelle-Video API Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host để gắn server")
    parser.add_argument("--port", type=int, default=8000, help="Port để gắn server")
    parser.add_argument("--reload", action="store_true", help="Bật tự động reload")

    args = parser.parse_args()

    # In banner khởi động
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                    Pixelle-Video API Server                      ║
╚══════════════════════════════════════════════════════════════╝

Đang khởi động server tại http://{args.host}:{args.port}
API Docs: http://{args.host}:{args.port}/docs
ReDoc: http://{args.host}:{args.port}/redoc

Nhấn Ctrl+C để dừng server
""")

    # Khởi động server
    uvicorn.run(
        "api.app:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )

