"""公开的系统能力状态，不暴露任何密钥内容。"""
from fastapi import APIRouter

from app.config import settings
from app.utils import Result

router = APIRouter(prefix="/api/system", tags=["系统"])


def _configured(value: str) -> bool:
    normalized = (value or "").strip().lower()
    return bool(normalized and not normalized.startswith("your-") and normalized != "change-me")


@router.get("/capabilities", summary="获取可用能力")
async def capabilities():
    llm = _configured(settings.LLM_API_KEY)
    return Result.success({
        "text_generation": {"available": llm, "fallback": True},
        "image_generation": {"available": _configured(settings.IMAGE_API_KEY), "fallback": False},
        "vision": {"available": _configured(settings.VISION_API_KEY), "fallback": False},
        "video_generation": {"available": _configured(settings.VIDEO_API_KEY), "fallback": False},
        "assistant": {"available": llm, "fallback": True},
        "imagery_analysis": {"available": llm, "fallback": True},
    })
