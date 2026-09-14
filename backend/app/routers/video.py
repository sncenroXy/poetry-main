"""诗境动画路由"""
from fastapi import APIRouter
from app.models import VideoGenerateRequest
from app.utils import Result
from app.services import video_service

router = APIRouter(prefix="/api/video", tags=["诗境动画"])


@router.post("/generate", summary="提交视频生成任务", response_model=Result)
async def generate_video(req: VideoGenerateRequest):
    """提交诗词文生视频任务，返回 task_id 用于轮询"""
    try:
        result = await video_service.submit_video_task(
            poem_text=req.poem_text,
            title=req.title,
            style=req.style,
        )
        return Result.success(result)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Video generation submit failed: %s", e)
        return Result.error("视频生成任务提交失败，请稍后再试")


@router.get("/status/{task_id}", summary="查询视频生成状态", response_model=Result)
async def video_status(task_id: str):
    """轮询视频生成任务状态"""
    try:
        result = await video_service.query_video_task(task_id)
        return Result.success(result)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Video status query failed: %s", e)
        return Result.error("查询视频状态失败，请稍后再试")
