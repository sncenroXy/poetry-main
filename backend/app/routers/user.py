"""用户中心：资料、收藏、学习记录、创作记录和推荐。"""
from fastapi import APIRouter, Depends, Query

from app.database import users_collection
from app.models import CreationRecordRequest, LearningEventRequest, PasswordChangeRequest, UserProfileUpdate, WrongAnswerRequest
from app.services import challenge_service, user_service
from app.utils import Result
from app.utils.auth import get_current_user, hash_password, verify_password

router = APIRouter(
    prefix="/api/user",
    tags=["用户中心"],
    dependencies=[Depends(get_current_user)],
)


@router.get("/profile", summary="用户资料")
async def profile(username: str = Depends(get_current_user)):
    return Result.success(await user_service.get_profile(username))


@router.put("/profile", summary="更新用户资料")
async def update_profile(body: UserProfileUpdate, username: str = Depends(get_current_user)):
    return Result.success(await user_service.update_profile(username, body))


@router.put("/password", summary="修改密码")
async def change_password(body: PasswordChangeRequest, username: str = Depends(get_current_user)):
    doc = await users_collection.find_one({"_id": username}, {"password_hash": 1})
    if not doc or not verify_password(body.current_password, doc.get("password_hash", "")):
        return Result.error("当前密码错误")
    if body.current_password == body.new_password:
        return Result.error("新密码不能与当前密码相同")
    await users_collection.update_one(
        {"_id": username},
        {"$set": {"password_hash": hash_password(body.new_password)}},
    )
    return Result.success()


@router.get("/favorites", summary="收藏列表")
async def favorites(
    limit: int = Query(50, ge=1, le=100),
    username: str = Depends(get_current_user),
):
    return Result.success(await user_service.list_favorites(username, limit))


@router.get("/favorites/{poem_id}/status", summary="收藏状态")
async def favorite_status(poem_id: str, username: str = Depends(get_current_user)):
    return Result.success({"favorited": await user_service.favorite_status(username, poem_id)})


@router.post("/favorites/{poem_id}", summary="收藏诗词")
async def add_favorite(poem_id: str, username: str = Depends(get_current_user)):
    if not await user_service.add_favorite(username, poem_id):
        return Result.error("诗词不存在")
    return Result.success({"favorited": True})


@router.delete("/favorites/{poem_id}", summary="取消收藏")
async def remove_favorite(poem_id: str, username: str = Depends(get_current_user)):
    await user_service.remove_favorite(username, poem_id)
    return Result.success({"favorited": False})


@router.post("/history/{poem_id}", summary="记录浏览")
async def record_history(poem_id: str, username: str = Depends(get_current_user)):
    if not await user_service.record_view(username, poem_id):
        return Result.error("诗词不存在")
    return Result.success()


@router.get("/history", summary="浏览历史")
async def history(
    limit: int = Query(20, ge=1, le=100),
    username: str = Depends(get_current_user),
):
    return Result.success(await user_service.list_history(username, limit))


@router.post("/learning/events", summary="记录练习结果")
async def learning_event(body: LearningEventRequest, username: str = Depends(get_current_user)):
    await user_service.record_learning_event(username, body)
    return Result.success()


@router.get("/learning/summary", summary="学习统计")
async def summary(username: str = Depends(get_current_user)):
    return Result.success(await user_service.learning_summary(username))


@router.post("/learning/adaptive-quiz", summary="根据薄弱题型生成自适应练习")
async def adaptive_quiz(
    count: int = Query(5, ge=1, le=10),
    username: str = Depends(get_current_user),
):
    stats = await user_service.learning_summary(username)
    focus_types = [item["type"] for item in stats["weak_points"]]
    data = await challenge_service.ai_generate_quiz(count, focus_types=focus_types)
    return Result.success({"items": data, "focus_types": focus_types[:3]})


@router.post("/creations", summary="保存创作记录")
async def save_creation(body: CreationRecordRequest, username: str = Depends(get_current_user)):
    return Result.success(await user_service.save_creation(username, body))


@router.get("/creations", summary="创作记录")
async def creations(
    limit: int = Query(30, ge=1, le=100),
    username: str = Depends(get_current_user),
):
    return Result.success(await user_service.list_creations(username, limit))


@router.get("/recommendations", summary="个性化诗词推荐")
async def recommendations(
    limit: int = Query(6, ge=1, le=20),
    username: str = Depends(get_current_user),
):
    return Result.success(await user_service.recommendations(username, limit))


@router.get("/portrait", summary="用户画像")
async def portrait(username: str = Depends(get_current_user)):
    return Result.success(await user_service.portrait(username))


# ---------- 错题本 ----------

@router.get("/wrong-answers", summary="错题本列表")
async def wrong_answers(
    limit: int = Query(50, ge=1, le=100),
    username: str = Depends(get_current_user),
):
    return Result.success(await user_service.list_wrong_answers(username, limit))


@router.post("/wrong-answers", summary="收录错题")
async def add_wrong_answer(body: WrongAnswerRequest, username: str = Depends(get_current_user)):
    return Result.success(await user_service.add_wrong_answer(username, body))


@router.delete("/wrong-answers/{wrong_id}", summary="删除单条错题")
async def remove_wrong_answer(wrong_id: str, username: str = Depends(get_current_user)):
    removed = await user_service.remove_wrong_answer(username, wrong_id)
    return Result.success({"removed": removed})


@router.delete("/wrong-answers", summary="清空错题本")
async def clear_wrong_answers(username: str = Depends(get_current_user)):
    return Result.success({"cleared": await user_service.clear_wrong_answers(username)})
