"""诗境漫游路由：/api/imagery/*（需登录）"""
import logging
from fastapi import APIRouter, Depends
from app.services import imagery_service
from app.models import ImageryAnalyzeRequest
from app.utils import Result
from app.utils.auth import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/imagery", tags=["诗境漫游"], dependencies=[Depends(get_current_user)])


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
