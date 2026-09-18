"""用户鉴权：密码哈希 + JWT 签发/校验 + FastAPI 依赖

密码用标准库 pbkdf2_hmac（加盐 + 常量时间比较），无需额外依赖；
token 用 pyjwt 签发的无状态 JWT，前端存 localStorage，请求时带 Authorization: Bearer <token>。
"""
import hashlib
import secrets
import time
from typing import Optional

import jwt
from fastapi import Header, HTTPException

from app.config import settings

_ITERATIONS = 100_000


def hash_password(password: str) -> str:
    """加盐哈希密码，返回 "salt$hex" 格式"""
    salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), _ITERATIONS)
    return f"{salt}${dk.hex()}"


def verify_password(password: str, stored: str) -> bool:
    """校验密码，常量时间比较防时序攻击"""
    try:
        salt, expected = stored.split("$", 1)
    except ValueError:
        return False
    dk = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), _ITERATIONS)
    return secrets.compare_digest(dk.hex(), expected)


def create_access_token(username: str) -> str:
    """签发 JWT，sub=username，带过期时间"""
    now = int(time.time())
    payload = {
        "sub": username,
        "iat": now,
        "exp": now + settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    """解析 JWT，返回 username；无效/过期返回 None"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


async def get_current_user(authorization: Optional[str] = Header(None)) -> str:
    """FastAPI 依赖：从 Authorization: Bearer <token> 解析用户名，失败抛 401"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="未登录或登录已过期")
    username = decode_access_token(authorization[7:].strip())
    if not username:
        raise HTTPException(status_code=401, detail="登录已过期，请重新登录")
    return username
