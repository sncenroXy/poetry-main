"""检索路由：/api/search, /api/poems, /api/authors"""
from typing import Optional, List
from fastapi import APIRouter, Query
from app.services import search_service
from app.models import Poem
from app.utils import Result

router = APIRouter(prefix="/api", tags=["检索"])


@router.get("/search", summary="通用检索（分页）")
async def search(
    q: Optional[str] = Query(None, description="查询关键词（诗句/诗名/作者/意象）"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(18, ge=1, le=100, description="每页条数"),
):
    poems, total = await search_service.search_poems(q, page, page_size)
    return Result.success({"items": poems, "total": total, "page": page, "page_size": page_size})


@router.get("/poems/filters", summary="获取诗词筛选项（朝代、体裁、作者、标签）")
async def get_filters():
    options = await search_service.get_filter_options()
    return Result.success(options)


@router.get("/poems", summary="列出所有诗词（分页，支持分类筛选）")
async def list_all(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(18, ge=1, le=100, description="每页条数"),
    dynasty: Optional[str] = Query(None, description="按朝代筛选"),
    genre: Optional[str] = Query(None, description="按体裁筛选"),
    author: Optional[str] = Query(None, description="按作者筛选"),
    tag: Optional[str] = Query(None, description="按标签筛选"),
):
    poems, total = await search_service.find_poems_filtered(
        page, page_size, dynasty=dynasty, genre=genre, author=author, tag=tag
    )
    return Result.success({"items": poems, "total": total, "page": page, "page_size": page_size})


@router.get("/poems/{poem_id}", summary="诗词详情（简洁）", response_model=Result[Poem])
async def get_poem(poem_id: str):
    """列表页快速查看诗词。另有 /api/poem/{id}/detail 用于鉴赏页"""
    poem = await search_service.find_poem_by_id(poem_id)
    if not poem:
        return Result.error("poem not found")
    return Result.success(poem)


@router.get("/authors/{name}/poems", summary="根据作者名检索诗词（分页）")
async def poems_by_author(
    name: str,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(18, ge=1, le=100, description="每页条数"),
):
    poems, total = await search_service.find_poems_by_author(name, page, page_size)
    return Result.success({"items": poems, "total": total, "page": page, "page_size": page_size})
