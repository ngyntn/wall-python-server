import os
import httpx
from io import BytesIO
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY")
HF_TOKEN = os.getenv("HF_API_TOKEN")
UNSPLASH_API_URL = "https://api.unsplash.com"

# Kích thước chuẩn cho Wallpaper Android
ANDROID_WIDTH = 1080
ANDROID_HEIGHT = 1920


# --- Helper function để lọc rác ---
def simplify_unsplash_data(data, is_search=False):
    """
    Hàm này chỉ lấy ID và URL ảnh, bỏ hết thông tin rác.
    """
    items = data["results"] if is_search else data
    simplified_list = []

    for item in items:
        # Lấy URL ảnh gốc từ Unsplash
        raw_url = item["urls"]["raw"]

        # Tạo URL tối ưu cho Mobile (thêm param resize ngay tại đây)
        # thumb: nhỏ gọn để load list nhanh
        thumb_url = f"{item['urls']['small']}&q=80"

        # full: kích thước chuẩn màn hình điện thoại
        full_url = f"{raw_url}&w={ANDROID_WIDTH}&h={ANDROID_HEIGHT}&fit=crop&q=85"

        obj = {
            "id": item["id"],
            "thumb_url": thumb_url,
            "full_url": full_url
        }
        simplified_list.append(obj)

    return simplified_list


# --- Các hàm Service chính ---

async def search_unsplash(query: str, page: int = 1):
    url = f"{UNSPLASH_API_URL}/search/photos"
    params = {
        "query": query,
        "page": page,
        "per_page": 20,
        "client_id": UNSPLASH_KEY,
        "orientation": "portrait"
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        # Gọi hàm lọc dữ liệu trước khi trả về
        return simplify_unsplash_data(resp.json(), is_search=True)


async def get_random_unsplash(tag: str = None):
    url = f"{UNSPLASH_API_URL}/photos/random"
    params = {
        "count": 20,
        "client_id": UNSPLASH_KEY,
        "orientation": "portrait"
    }
    if tag and tag != "Popular":
        params["query"] = tag

    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        # Gọi hàm lọc dữ liệu trước khi trả về
        return simplify_unsplash_data(resp.json(), is_search=False)


async def download_image_proxy(url: str):
    # Logic download giữ nguyên vì Android cần bytes file
    async with httpx.AsyncClient() as client:
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.content


def generate_image_hf(prompt: str):
    client = InferenceClient(
        provider="nscale",
        api_key=HF_TOKEN
    )

    IMG_WIDTH = 768
    IMG_HEIGHT = 1344
    enhanced_prompt = f"{prompt}, vertical wallpaper, mobile background, 8k resolution, centered composition"

    try:
        image = client.text_to_image(
            enhanced_prompt,
            model="stabilityai/stable-diffusion-xl-base-1.0",
            width=IMG_WIDTH,
            height=IMG_HEIGHT
        )

        img_byte_arr = BytesIO()
        image.save(img_byte_arr, format='PNG')
        img_byte_arr.seek(0)
        return img_byte_arr.getvalue()

    except Exception as e:
        print(f"Error generating image: {e}")
        return None