"""诗境动画服务 — 文生视频（智谱 CogVideoX）"""
import logging
import asyncio
from typing import Optional, Dict, Any
import httpx
from openai import AsyncOpenAI
from app.config import settings

logger = logging.getLogger(__name__)

# ---------- 客户端惰性初始化 ----------

_llm_client: Optional[AsyncOpenAI] = None
_video_api_key: str = ""


def _get_llm_client() -> AsyncOpenAI:
    """复用现有文本 LLM 客户端"""
    global _llm_client
    if _llm_client is None:
        _llm_client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
    return _llm_client


# ---------- Prompt 翻译 ----------

VIDEO_PROMPT_SYSTEM = """你是一位精通中国古典诗词与影视艺术的翻译专家。
你的任务是将中国古典诗词翻译为适合 AI 视频生成模型的英文画面描述 prompt。

要求：
1. 深入理解诗词的意境、情感和视觉元素
2. 描述一个连续的动态画面场景（适合短视频），包含景物运动、光影变化、氛围流转
3. 始终附加风格关键词：Chinese ink wash painting style, traditional landscape, flowing brushwork, cinematic camera movement, ethereal atmosphere
4. prompt 长度控制在 80-150 个英文单词
5. 只返回英文 prompt 文本，不要任何其他内容"""


async def _translate_poem_to_video_prompt(poem_text: str, title: str = "", style: str = "水墨国风") -> str:
    """用 LLM 将诗词翻译为视频生成 prompt"""
    user_msg = f"诗词标题：{title}\n诗词内容：\n{poem_text}"
    if style != "水墨国风":
        user_msg += f"\n画面风格偏好：{style}"

    llm = _get_llm_client()
    resp = await llm.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": VIDEO_PROMPT_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.7,
        max_tokens=300,
    )
    return (resp.choices[0].message.content or "").strip()


# ---------- 智谱 CogVideoX API ----------

async def submit_video_task(poem_text: str, title: str = "", style: str = "水墨国风") -> Dict[str, Any]:
    """提交视频生成任务

    Returns:
        {"task_id": str, "prompt_used": str, "status": "processing"}
    """
    # 第 1 步：翻译诗词为英文视频 prompt
    video_prompt = await _translate_poem_to_video_prompt(poem_text, title, style)
    logger.info("Video prompt translated: %s", video_prompt[:200])

    # 第 2 步：提交视频生成任务到智谱 API
    api_key = settings.VIDEO_API_KEY
    base_url = settings.VIDEO_BASE_URL.rstrip("/")
    model = settings.VIDEO_MODEL

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(
            f"{base_url}/videos/generations",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "prompt": video_prompt,
            },
        )
        resp.raise_for_status()
        data = resp.json()

    task_id = data.get("id", "")
    if not task_id:
        raise ValueError(f"No task_id in response: {data}")

    logger.info("Video task submitted: %s", task_id)

    return {
        "task_id": task_id,
        "prompt_used": video_prompt,
        "status": "processing",
        "poem_text": poem_text,
        "title": title,
    }


async def query_video_task(task_id: str) -> Dict[str, Any]:
    """查询视频生成任务状态

    Returns:
        {"task_id": str, "status": "processing"|"completed"|"failed", "video_url": str|None}
    """
    api_key = settings.VIDEO_API_KEY
    base_url = settings.VIDEO_BASE_URL.rstrip("/")

    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.get(
            f"{base_url}/async-result/{task_id}",
            headers={
                "Authorization": f"Bearer {api_key}",
            },
        )
        resp.raise_for_status()
        data = resp.json()

    task_status = data.get("task_status", "PROCESSING")

    if task_status == "SUCCESS":
        # 从 video_result 中提取视频 URL
        video_results = data.get("video_result", [])
        video_url = ""
        if video_results and isinstance(video_results, list):
            video_url = video_results[0].get("url", "")
        elif isinstance(video_results, dict):
            video_url = video_results.get("url", "")

        # 兜底：尝试其他字段
        if not video_url:
            for key in ("video_url", "url", "result"):
                if key in data and isinstance(data[key], str) and data[key].startswith("http"):
                    video_url = data[key]
                    break

        return {
            "task_id": task_id,
            "status": "completed",
            "video_url": video_url,
        }
    elif task_status == "FAIL":
        return {
            "task_id": task_id,
            "status": "failed",
            "video_url": None,
        }
    else:
        # PROCESSING or other
        return {
            "task_id": task_id,
            "status": "processing",
            "video_url": None,
        }
