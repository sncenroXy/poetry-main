"""AI 诗词助手路由：/api/assistant/*"""
from fastapi import APIRouter
from app.services import assistant_service
from app.models import AssistantChatRequest
from app.utils import Result

router = APIRouter(prefix="/api/assistant", tags=["AI 助手"])


@router.post("/chat", summary="AI 诗词助手对话")
async def chat(req: AssistantChatRequest):
    data = await assistant_service.chat(req)
    return Result.success(data)
