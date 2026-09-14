"""生成路由：/api/generate/*"""
from fastapi import APIRouter
from app.services import generation_service
from app.models import Poem, GenerationRequest, OptimizeRequest
from app.utils import Result
from typing import List

router = APIRouter(prefix="/api/generate", tags=["生成"])


@router.post("", summary="生成诗词（多版本）", response_model=Result[List[Poem]])
async def generate(req: GenerationRequest):
    data = await generation_service.generate_poems(req)
    return Result.success(data)


@router.post("/optimize", summary="对已生成诗词进行轻度优化", response_model=Result[Poem])
async def optimize(body: OptimizeRequest):
    poem = await generation_service.optimize_poem(body.id)
    if not poem:
        return Result.error("poem not found")
    return Result.success(poem)


@router.post("/mimic", summary="仿写：提供草稿文本", response_model=Result[Poem])
async def mimic(req: GenerationRequest):
    if not req.draft:
        return Result.error("invalid request: draft is required")
    poem = await generation_service.mimic_poem(req)
    if not poem:
        return Result.error("mimic failed")
    return Result.success(poem)
