"""LLM 相关通用工具函数"""
import json
import logging
import re
from typing import Any

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


# ---------- OpenAI 兼容客户端（统一工厂：超时 + 重试） ----------

_llm_client = None
_image_client = None
_vision_client = None


def _build_client(api_key: str, base_url: str) -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=api_key,
        base_url=base_url,
        timeout=60.0,
        max_retries=2,
    )


def get_llm_client() -> AsyncOpenAI:
    """文本 LLM 客户端（生成/润色/仿写/飞花令/答题/助手/意象等复用）"""
    global _llm_client
    if _llm_client is None:
        _llm_client = _build_client(settings.LLM_API_KEY, settings.LLM_BASE_URL)
    return _llm_client


def get_image_client() -> AsyncOpenAI:
    """图像生成 API 客户端"""
    global _image_client
    if _image_client is None:
        _image_client = _build_client(settings.IMAGE_API_KEY, settings.IMAGE_BASE_URL)
    return _image_client


def get_vision_client() -> AsyncOpenAI:
    """视觉模型 API 客户端"""
    global _vision_client
    if _vision_client is None:
        _vision_client = _build_client(settings.VISION_API_KEY, settings.VISION_BASE_URL)
    return _vision_client


def parse_llm_json(raw: str) -> Any:
    """从 LLM 返回的文本中提取 JSON，支持 markdown 代码块容错

    尝试策略：
    1. 去除 markdown 代码块后直接 json.loads
    2. 使用正则按字段名边界提取（针对格式不完整的情况）
    """
    text = raw.strip()
    # 去除 markdown 代码块
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    if text.startswith("json"):
        text = text[4:].strip()

    # 第一次尝试：直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 第二次尝试：用字段名作为边界切割
    logger.warning("Standard JSON parse failed, trying field extraction: %s", text[:300])
    known_keys = [
        "title", "genre", "content", "scene_description",
        "translation", "appreciation", "cultural",
        "hint", "level", "source_title",
        "correct", "explanation", "correct_answer", "source_author",
        "ai_answer", "ai_answer_title", "ai_answer_author",
        "new_line", "new_line_title", "new_line_author", "comment",
        "is_correct", "correct_option", "full_poem", "knowledge",
        "score_comment", "weak_points", "recommendations", "encouragement",
        "id", "type", "question", "options", "answer", "source",
    ]
    field_positions = []
    for key in known_keys:
        for m in re.finditer(rf'["\s{{]?{key}["\s:：]*', text):
            field_positions.append((m.start(), m.end(), key))
    field_positions.sort(key=lambda x: x[0])

    result = {}
    for i, (start, val_start, key) in enumerate(field_positions):
        if i + 1 < len(field_positions):
            val_end = field_positions[i + 1][0]
        else:
            val_end = len(text)
        val = text[val_start:val_end].strip().rstrip(",").rstrip("}").strip()

        if key == "content":
            m = re.search(r'\[([^\]]*)\]', val)
            if m:
                inner = m.group(1)
                lines = re.split(r'\s{2,}|,\s*', inner)
                result[key] = [l.strip().strip('"') for l in lines if l.strip().strip('"')]
            else:
                result[key] = [l.strip() for l in val.split("\n") if l.strip()]
        else:
            val = val.strip('"').strip("'")
            result[key] = val

    if result:
        return result
    raise ValueError(f"Cannot parse LLM response: {text[:200]}")
