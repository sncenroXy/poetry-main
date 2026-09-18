"""AI 诗词助手路由：/api/assistant/*（需登录）"""
from fastapi import APIRouter, Depends
from app.services import assistant_service
from app.models import AssistantChatRequest
from app.utils import Result
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/assistant", tags=["AI 助手"], dependencies=[Depends(get_current_user)])


@router.post("/chat", summary="AI 诗词助手对话")
async def chat(req: AssistantChatRequest):
    data = await assistant_service.chat(req)
    return Result.success(data)
