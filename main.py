import uvicorn
import os
from fastapi import FastAPI, HTTPException, Response
import services
from models import AIRequest

import random # Import để random màu
import io     # Import để xử lý bytes
from PIL import Image, ImageDraw # Import để vẽ ảnh giả

app = FastAPI()


@app.get("/")
def read_root():
    return {"status": "running"}


@app.get("/api/wallpapers/search")
async def search_photos(query: str, page: int = 1):
    try:
        return await services.search_unsplash(query, page)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wallpapers/random")
async def random_photos(tag: str = None):
    try:
        return await services.get_random_unsplash(tag)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/wallpapers/download")
async def download_photo(url: str):
    if not url:
        raise HTTPException(status_code=400, detail="Missing URL")
    try:
        image_bytes = await services.download_image_proxy(url)
        return Response(content=image_bytes, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/generate")
def generate_ai(request: AIRequest):
    # image_bytes = services.generate_image_hf(request.prompt)
    #
    # if image_bytes:
    #     return Response(content=image_bytes, media_type="image/png")
    # else:
    #     raise HTTPException(status_code=500, detail="Generation Failed")
    print(f"🛠️ [FAKE MODE] Đang giả lập tạo ảnh cho prompt: {request.prompt}")

    try:
        # 1. Tạo ảnh màu ngẫu nhiên (Kích thước chuẩn Mobile)
        width = 768
        height = 1344
        # Random màu RGB
        color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))

        # Tạo ảnh mới bằng Pillow
        img = Image.new('RGB', (width, height), color=color)

        # (Tuỳ chọn) Vẽ một hình chữ nhật ở giữa để nhìn cho đỡ chán
        draw = ImageDraw.Draw(img)
        draw.rectangle(
            [(100, 400), (width - 100, height - 400)],
            outline="white",
            width=5
        )

        # 2. Chuyển đổi ảnh thành Bytes (giả lập y hệt API thật trả về)
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='PNG')
        fake_image_bytes = img_byte_arr.getvalue()

        # 3. Trả về Client
        return Response(content=fake_image_bytes, media_type="image/png")

    except Exception as e:
        print(f"Lỗi khi tạo ảnh fake: {e}")
        raise HTTPException(status_code=500, detail="Fake Generation Failed")


if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host=host, port=port)