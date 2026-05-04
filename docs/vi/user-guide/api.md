# Sử dụng API

Pixelle-Video cung cấp Python API đầy đủ để dễ dàng tích hợp vào dự án của bạn.

---

## Bắt đầu nhanh

```python
from pixelle_video.service import PixelleVideoCore
import asyncio

async def main():
    # Khởi tạo
    pixelle = PixelleVideoCore()
    await pixelle.initialize()
    
    # Sinh video
    result = await pixelle.generate_video(
        text="Why develop a reading habit",
        mode="generate",
        n_scenes=5
    )
    
    print(f"Video generated: {result.video_path}")

# Chạy
asyncio.run(main())
```

---

## Tham chiếu API

Để xem tài liệu API chi tiết, xem [Tổng quan API](../reference/api-overview.md).

---

## Ví dụ

Để xem thêm ví dụ sử dụng, xem thư mục `examples/` trong dự án.
