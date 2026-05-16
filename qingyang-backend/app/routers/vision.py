import io
import base64

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from PIL import Image

from app.config import settings
from app.schemas.vision import VisionResponse
from app.services.ai_client import AIService, AIServiceError
from app.services.meal_plan_parser import extract_json, VisionParseError
from app.dependencies import get_ai_service

router = APIRouter()

SYSTEM_PROMPT = (
    "你是'轻养AI'食物识别与营养分析专家。分析图片中的食物，提供以下信息：\n"
    "1. 食物名称\n"
    "2. 预估热量（千卡）\n"
    "3. 健康评价（基于营养学角度）\n"
    "4. 食用建议\n\n"
    "你必须严格以 JSON 格式输出，不包含 markdown 标记、代码栅栏或额外说明：\n"
    "{\n"
    '  "food_name": "...",\n'
    '  "estimated_calories": "...",\n'
    '  "health_evaluation": "...",\n'
    '  "suggestions": "..."\n'
    "}"
)

# Map FastAPI content_type to Pillow format and file extension
CONTENT_TYPE_MAP = {
    "image/jpeg": ("JPEG", "jpeg"),
    "image/png": ("PNG", "png"),
    "image/webp": ("WEBP", "webp"),
}

MAX_IMAGE_DIMENSION = 1024  # Longest side limit in px


async def _read_and_compress_image(file: UploadFile) -> str:
    """Validate, resize, and compress uploaded image, return base64 JPEG string."""
    # 1. Validate content type
    if file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail="不支持的图片格式，请上传 JPG、PNG 或 WEBP 格式的图片",
        )

    # 2. Read raw bytes
    raw_bytes = await file.read()
    if len(raw_bytes) > settings.MAX_IMAGE_SIZE_MB * 1024 * 1024:
        raise HTTPException(
            status_code=400,
            detail=f"图片文件过大，请上传小于 {settings.MAX_IMAGE_SIZE_MB}MB 的图片",
        )

    # 3. Open with Pillow and resize
    try:
        img = Image.open(io.BytesIO(raw_bytes))
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="无法解析图片文件，请确认图片未损坏",
        )

    # Convert RGBA/P to RGB for JPEG compression
    if img.mode in ("RGBA", "P"):
        img = img.convert("RGB")

    # Proportional resize: limit longest side to MAX_IMAGE_DIMENSION
    width, height = img.size
    if max(width, height) > MAX_IMAGE_DIMENSION:
        ratio = MAX_IMAGE_DIMENSION / max(width, height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)
        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # 4. Compress to medium-quality JPEG and encode as base64
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=85, optimize=True)
    b64_str = base64.b64encode(buffer.getvalue()).decode("utf-8")
    return f"data:image/jpeg;base64,{b64_str}"


@router.post("/api/vision/recognize")
async def recognize_food(
    file: UploadFile = File(...),
    ai_service: AIService = Depends(get_ai_service),
):
    """
    Upload a food photo for AI recognition.
    Accepts multipart/form-data with a single image file.
    """
    # 1. Process image (validate, resize, compress → base64)
    try:
        base64_image = await _read_and_compress_image(file)
    except HTTPException:
        raise  # Re-raise validation errors directly
    except Exception:
        return JSONResponse(
            status_code=400,
            content={"detail": "图片处理失败，请重试"},
        )

    # 2. Build multimodal messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "请识别这张图片中的食物并给出营养分析"},
                {
                    "type": "image_url",
                    "image_url": {"url": base64_image},
                },
            ],
        },
    ]

    # 3. Call AI
    try:
        raw = await ai_service.respond(
            messages=messages,
            temperature=0.3,
            max_tokens=2048,
        )
    except AIServiceError as e:
        return JSONResponse(
            status_code=502,
            content={"detail": e.message},
        )

    # 4. Parse response
    try:
        data = extract_json(raw)
        return VisionResponse.model_validate(data)
    except (VisionParseError, Exception):
        return JSONResponse(
            status_code=502,
            content={"detail": "图片识别失败，请更换图片后重试"},
        )
