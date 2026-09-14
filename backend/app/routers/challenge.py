"""挑战路由：/api/challenge/*"""
from fastapi import APIRouter, Query
from app.services import challenge_service
from app.models import (
    ValidateRequest,
    ChainHintRequest, ChainAIValidateRequest, ChainAITurnRequest,
    QuizExplainRequest, QuizSummaryRequest,
)
from app.utils import Result

router = APIRouter(prefix="/api/challenge", tags=["挑战"])


# ---------- 原有端点 ----------

@router.get("/chain/next", summary="查找给定诗句的下句候选")
async def next_line(line: str = Query(..., description="完整诗句", example="床前明月光")):
    data = await challenge_service.find_next_lines(line)
    return Result.success(data)


@router.post("/chain/validate", summary="校验接龙答案是否正确（精确匹配）")
async def validate_chain(body: ValidateRequest):
    ok = await challenge_service.validate_chain(body.current, body.answer)
    return Result.success({"correct": ok})


@router.get("/quiz", summary="生成填空选择题（数据库）")
async def quiz(count: int = Query(3, ge=1, le=10, description="题目数量")):
    data = await challenge_service.generate_quiz(count)
    return Result.success(data)


# ---------- AI 增强端点 ----------

@router.post("/chain/ai-hint", summary="飞花令 AI 渐进提示")
async def chain_ai_hint(body: ChainHintRequest):
    data = await challenge_service.ai_hint(body.line, body.level)
    return Result.success(data)


@router.post("/chain/ai-validate", summary="飞花令 AI 语义校验")
async def chain_ai_validate(body: ChainAIValidateRequest):
    data = await challenge_service.ai_validate_chain(body.current, body.answer)
    return Result.success(data)


@router.post("/chain/ai-turn", summary="飞花令 AI 对战回合")
async def chain_ai_turn(body: ChainAITurnRequest):
    data = await challenge_service.ai_chain_turn(body.current)
    return Result.success(data)


@router.post("/quiz/ai-generate", summary="AI 生成多种题型")
async def quiz_ai_generate(count: int = Query(5, ge=1, le=10, description="题目数量")):
    data = await challenge_service.ai_generate_quiz(count)
    return Result.success(data)


@router.post("/quiz/ai-explain", summary="AI 解析单题")
async def quiz_ai_explain(body: QuizExplainRequest):
    data = await challenge_service.ai_explain_answer(body.question, body.user_answer)
    return Result.success(data)


@router.post("/quiz/ai-summary", summary="AI 答题总结分析")
async def quiz_ai_summary(body: QuizSummaryRequest):
    data = await challenge_service.ai_quiz_summary(body.results)
    return Result.success(data)
