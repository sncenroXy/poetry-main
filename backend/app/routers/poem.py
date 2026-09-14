"""鉴赏路由：/api/poem/{id}/detail"""
from fastapi import APIRouter
from app.services import search_service
from app.models import Poem
from app.utils import Result

router = APIRouter(prefix="/api/poem", tags=["鉴赏"])


@router.get("/{poem_id}/detail", summary="鉴赏详情：原文、白话译文、赏析、文化拓展", response_model=Result[Poem])
async def poem_detail(poem_id: str):
    poem = await search_service.find_poem_by_id(poem_id)
    if not poem:
        return Result.error("poem not found")
    return Result.success(poem)
