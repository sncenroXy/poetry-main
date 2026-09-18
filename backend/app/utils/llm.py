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


async def chat_json(
    system: str,
    user: str,
    temperature: float = 0.7,
    max_tokens: int = 2000,
    client: AsyncOpenAI | None = None,
) -> str:
    """调用 LLM 并要求 JSON 输出，返回原始文本（仍需 parse_llm_json 解析）。

    优先传 response_format={"type": "json_object"} 让模型直接输出合法 JSON；
    部分 OpenAI 兼容接口不支持该参数，会自动降级重试。
    """
    client = client or get_llm_client()
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    kwargs = dict(model=settings.LLM_MODEL, messages=messages, temperature=temperature, max_tokens=max_tokens)
    try:
        resp = await client.chat.completions.create(**kwargs, response_format={"type": "json_object"})
    except Exception as e:
        logger.warning("response_format=json_object unsupported, retrying without it: %s", e)
        resp = await client.chat.completions.create(**kwargs)
    return (resp.choices[0].message.content or "").strip()


def _strip_fences(text: str) -> str:
    """去除 markdown 代码块包裹及 ``json`` 前缀"""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    if text.lower().startswith("json"):
        text = text[4:].strip()
    return text


def _extract_json_slice(text: str) -> str:
    """定位首个 { 或 [ 到最后一个 } 或 ]，容忍 JSON 前后的废话"""
    start = -1
    end = -1
    for i, ch in enumerate(text):
        if ch in "{[":
            start = i
            break
    for i in range(len(text) - 1, -1, -1):
        if text[i] in "}]":
            end = i
            break
    if start != -1 and end > start:
        return text[start:end + 1]
    return ""


def parse_llm_json(raw: str) -> Any:
    """从 LLM 返回的文本中提取 JSON，多级容错：

    1. 去除 markdown 代码块后直接 json.loads
    2. 定位首 { / [ 到末 } / ] 切片后 json.loads（容忍前后废话）
    3. json5 宽松解析（容忍尾逗号/单引号/注释）
    4. 正则按字段名边界提取（最后兜底，针对格式不完整的情况）
    """
    text = _strip_fences(raw)

    # 1) 直接解析
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2) 括号切片解析（容忍 JSON 前后的说明文字）
    sliced = _extract_json_slice(text)
    if sliced and sliced != text:
        try:
            return json.loads(sliced)
        except json.JSONDecodeError:
            pass

    # 3) json5 宽松解析
    try:
        import json5
        return json5.loads(sliced or text)
    except Exception:
        pass

    # 4) 正则字段提取兜底
    logger.warning("JSON parse failed, falling back to field extraction: %s", text[:300])
    return _parse_json_by_fields(text)


def _parse_json_by_fields(text: str) -> Any:
    """正则按字段名边界切割（针对格式不完整、无法整体解析的情况）"""
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
