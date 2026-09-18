"""安全中间件：AI 接口鉴权 + 按 IP 限流

针对成本敏感的 AI 接口（文本/图像/视频/助手/意象）：
1. 当配置了 APP_API_KEY 时，校验 X-API-Key 请求头；
2. 按客户端 IP 做滑动窗口限流，图/视频接口更严格。

说明：
- 限流器为进程内实现，适用于单容器/单进程部署；多副本部署需换成 Redis 等共享存储。
- 客户端 IP 优先取 X-Forwarded-For（Nginx 已设置），回退 X-Real-IP，再回退直连地址。
"""
import logging
import time
from collections import defaultdict, deque
from typing import Deque, Dict

from fastapi import Request
from fastapi.responses import JSONResponse

from app.config import settings

logger = logging.getLogger(__name__)

# 需要鉴权/限流的 AI 接口前缀（成本敏感）
PROTECTED_PREFIXES = (
    "/api/generate",
    "/api/image",
    "/api/video",
    "/api/assistant",
    "/api/imagery",
    "/api/challenge/chain/ai-",
    "/api/challenge/quiz/ai-",
)

_MEDIA_PREFIXES = ("/api/image", "/api/video")


def _is_protected(path: str) -> bool:
    return path.startswith(PROTECTED_PREFIXES)


def _is_media(path: str) -> bool:
    return path.startswith(_MEDIA_PREFIXES)


class SimpleRateLimiter:
    """基于滑动窗口的进程内限流器"""

    def __init__(self) -> None:
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._last_cleanup = time.monotonic()
        self._cleanup_interval = 60.0

    def _cleanup_if_needed(self) -> None:
        now = time.monotonic()
        if now - self._last_cleanup < self._cleanup_interval:
            return
        self._last_cleanup = now
        stale = [key for key, dq in self._hits.items() if not dq]
        for key in stale:
            self._hits.pop(key, None)

    def allow(self, key: str, limit: int, window: float = 60.0) -> bool:
        """返回该 key 是否仍在限流额度内。limit<=0 视为不限流。"""
        if limit <= 0:
            return True
        now = time.monotonic()
        self._cleanup_if_needed()
        dq = self._hits[key]
        while dq and dq[0] <= now - window:
            dq.popleft()
        if len(dq) >= limit:
            return False
        dq.append(now)
        return True


_rate_limiter = SimpleRateLimiter()


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("x-real-ip")
    if real_ip:
        return real_ip.strip()
    return request.client.host if request.client else "unknown"


async def security_middleware(request: Request, call_next):
    path = request.url.path
    if not _is_protected(path):
        return await call_next(request)

    # 1) API Key 鉴权（仅当配置了 APP_API_KEY 时启用，避免误伤开发环境）
    if settings.APP_API_KEY:
        provided = request.headers.get("x-api-key", "")
        if provided != settings.APP_API_KEY:
            logger.warning("API key auth failed: ip=%s path=%s", _client_ip(request), path)
            return JSONResponse(
                status_code=403,
                content={"code": 0, "msg": "缺少或无效的 API Key", "data": None},
            )

    # 2) 按 IP 限流（图/视频更严格；文本与图/视频分开计数，避免互相干扰）
    ip = _client_ip(request)
    is_media = _is_media(path)
    limit = (
        settings.MEDIA_RATE_LIMIT_PER_MINUTE
        if is_media
        else settings.AI_RATE_LIMIT_PER_MINUTE
    )
    key = f"{ip}:{'media' if is_media else 'text'}"
    if not _rate_limiter.allow(key, limit):
        logger.warning("Rate limited: ip=%s path=%s", ip, path)
        return JSONResponse(
            status_code=429,
            content={"code": 0, "msg": "请求过于频繁，请稍后再试", "data": None},
        )

    return await call_next(request)
