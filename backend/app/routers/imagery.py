"""诗境漫游路由：/api/imagery/*"""
import logging
from fastapi import APIRouter
from app.services import imagery_service
from app.models import ImageryAnalyzeRequest
from app.utils import Result

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/imagery", tags=["诗境漫游"])


@router.post("/analyze", summary="分析诗词意象")
async def analyze(req: ImageryAnalyzeRequest):
    try:
        data = await imagery_service.analyze(req)
        return Result.success(data)
    except Exception as e:
        logger.error("Imagery router unexpected error: %s", e)
        return Result.success({
            "poem_summary": f"「{req.title or '此诗'}」意境深远，值得细细品味。（AI 分析暂时不可用）",
            "imagery_nodes": [],
        })
