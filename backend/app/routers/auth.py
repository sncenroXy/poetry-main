"""认证路由：注册 / 登录 / 当前用户"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.database import users_collection
from app.utils import Result
from app.utils.auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/api/auth", tags=["认证"])


class AuthRequest(BaseModel):
    """注册/登录请求"""
    username: str = Field(..., min_length=3, max_length=32, description="用户名")
    password: str = Field(..., min_length=6, max_length=64, description="密码")


def _issue(username: str) -> dict:
    return {"token": create_access_token(username), "user": {"username": username}}


@router.post("/register", summary="注册")
async def register(body: AuthRequest):
    username = body.username.strip()
    if await users_collection.find_one({"_id": username}):
        return Result.error("用户名已存在")
    await users_collection.insert_one({
        "_id": username,
        "password_hash": hash_password(body.password),
    })
    return Result.success(_issue(username))


@router.post("/login", summary="登录")
async def login(body: AuthRequest):
    username = body.username.strip()
    doc = await users_collection.find_one({"_id": username})
    if not doc or not verify_password(body.password, doc.get("password_hash", "")):
        return Result.error("用户名或密码错误")
    return Result.success(_issue(username))


@router.get("/user", summary="当前用户信息")
async def me(username: str = Depends(get_current_user)):
    return Result.success({"username": username})
