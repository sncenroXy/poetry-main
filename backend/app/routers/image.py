"""诗画互生路由"""
from fastapi import APIRouter
from app.models import ImageGenerateRequest, ImagePoemRequest
from app.utils import Result
from app.services import image_service

router = APIRouter(prefix="/api/image", tags=["诗画互生"])


@router.post("/generate", summary="文生图：诗词生成配图", response_model=Result)
async def generate_image(req: ImageGenerateRequest):
    """将诗词文本转化为水墨国风配图"""
    try:
        result = await image_service.generate_image_from_poem(
            poem_text=req.poem_text,
            title=req.title,
            style=req.style,
        )
        return Result.success(result)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Image generation failed: %s", e)
        return Result.error("图片生成失败，请稍后再试")


@router.post("/poem", summary="图生文：图片生成诗词", response_model=Result)
async def generate_poem(req: ImagePoemRequest):
    """上传图片，AI 看图写诗"""
    try:
        result = await image_service.generate_poem_from_image(
            image_base64=req.image,
            style=req.style,
            emotion=req.emotion,
        )
        return Result.success(result)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Vision poem generation failed: %s", e)
        return Result.error("诗词生成失败，请稍后再试")
