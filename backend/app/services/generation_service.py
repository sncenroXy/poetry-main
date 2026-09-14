"""生成服务 — 基于 OpenAI 兼容 API"""
import logging
import time
from typing import List, Optional
from openai import AsyncOpenAI
from app.config import settings
from app.models import Poem, Author, Analysis, GenerationRequest
from app.database import poems_collection
from app.utils.llm import parse_llm_json

logger = logging.getLogger(__name__)

# 初始化 OpenAI 客户端（兼容中转站/NewAPI/OneAPI）
_client: Optional[AsyncOpenAI] = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
    return _client


async def _chat(system: str, user: str) -> str:
    """调用 LLM 并返回文本"""
    client = _get_client()
    resp = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=0.8,
        max_tokens=2000,
    )
    result = (resp.choices[0].message.content or "").strip()
    logger.debug("LLM raw response: %s", result[:500])
    return result


GENERATE_SYSTEM = """你是一位精通古典诗词的AI诗人。你能根据用户的场景、情感、风格和意象要求，创作高质量的中国古典诗词。

要求：
1. 严格按照指定的风格（唐诗/宋词/古风）创作
2. 融入用户指定的意象，语言优美自然
3. 注意平仄和韵律（尽量押韵）
4. 返回 JSON 格式，结构如下：
{
  "title": "诗词标题",
  "genre": "体裁（如五言绝句、七言律诗、词等）",
  "content": ["第一句", "第二句", "第三句", "第四句"],
  "translation": "白话译文",
  "appreciation": "简要赏析（50字以内）"
}

只返回 JSON，不要其他内容。"""

OPTIMIZE_SYSTEM = """你是一位古典诗词润色专家。你能对诗词进行精炼打磨，提升文学性和意境。

要求：
1. 保持原诗的情感和主题不变
2. 优化用词，使之更加精炼、雅致
3. 改善韵律和平仄
4. 返回 JSON 格式：
{
  "title": "润色后标题",
  "genre": "体裁",
  "content": ["第一句", "第二句", "第三句", "第四句"],
  "translation": "白话译文",
  "appreciation": "润色说明（改了什么，为什么）"
}

只返回 JSON，不要其他内容。"""

MIMIC_SYSTEM = """你是一位古典诗词仿写专家。你能根据用户提供的原诗或草稿，以指定的风格和情感进行仿写创作。

要求：
1. 仿写要体现原诗的结构和意境，但内容要有创新
2. 融合指定的情感基调
3. 按指定风格（唐诗/宋词/古风）创作
4. 返回 JSON 格式：
{
  "title": "仿写诗词标题",
  "genre": "体裁",
  "content": ["第一句", "第二句", "第三句", "第四句"],
  "translation": "白话译文",
  "appreciation": "仿写说明（参考了原诗哪些方面）"
}

只返回 JSON，不要其他内容。"""


async def generate_poems(req: GenerationRequest) -> List[Poem]:
    """生成诗词"""
    count = max(1, min(3, req.count))
    style = req.style or "古风"
    images = req.images if req.images else []

    results = []
    for i in range(count):
        # 优先使用自由描述 prompt
        if req.prompt and req.prompt.strip():
            user_prompt = f"{req.prompt.strip()}\n"
            if style:
                user_prompt += f"风格偏好：{style}\n"
            if req.emotion:
                user_prompt += f"情感基调：{req.emotion}\n"
            if images:
                user_prompt += f"可融入的意象：{'、'.join(images)}\n"
        else:
            scene = req.scene or "江南"
            emotion = req.emotion or "闲适"
            if not images:
                images = ["明月"]
            user_prompt = (
                f"请创作一首{style}。\n"
                f"场景：{scene}\n"
                f"情感基调：{emotion}\n"
                f"必须融入的意象：{'、'.join(images)}\n"
            )
        if count > 1:
            user_prompt += f"这是第 {i + 1}/{count} 首，请与前几首有所不同。\n"

        try:
            raw = await _chat(GENERATE_SYSTEM, user_prompt)
            data = parse_llm_json(raw)
            poem = _build_poem_from_llm(data, style, images, i + 1)
        except Exception as e:
            logger.warning("LLM generate failed (attempt %d): %s", i + 1, e)
            # LLM 失败时回退到简单模板
            fb_scene = req.scene or (req.prompt[:4] if req.prompt else "江南")
            fb_emotion = req.emotion or "闲适"
            fb_images = images if images else ["明月"]
            poem = _fallback_poem(fb_scene, fb_emotion, style, fb_images, i + 1)

        results.append(poem)

    return results


async def optimize_poem(poem_id: str) -> Optional[Poem]:
    """润色诗词"""
    # 从数据库获取原诗
    doc = await poems_collection.find_one({"_id": poem_id})
    if not doc:
        return None
    doc["id"] = doc.pop("_id")
    src = Poem(**doc)

    user_prompt = (
        f"请润色以下诗词：\n"
        f"标题：{src.title}\n"
        f"体裁：{src.genre or '古诗'}\n"
        f"原文：\n" + "\n".join(src.content)
    )

    try:
        raw = await _chat(OPTIMIZE_SYSTEM, user_prompt)
        data = parse_llm_json(raw)
        new_id = f"{poem_id}-opt-{int(time.time())}"
        poem = Poem(
            id=new_id,
            title=data.get("title", src.title),
            author=Author(name="AI润色", dynasty="现代", brief="基于原诗润色"),
            dynasty="现代",
            genre=data.get("genre", src.genre),
            content=data.get("content", src.content),
            analysis=Analysis(
                translation=data.get("translation", ""),
                appreciation=data.get("appreciation", ""),
                cultural="AI 润色结果，仅供参考。",
            ),
            tags=src.tags,
        )
    except Exception as e:
        logger.warning("LLM optimize failed for %s: %s", poem_id, e)
        # LLM 失败时做简单替换
        new_id = f"{poem_id}-opt-{int(time.time())}"
        poem = Poem(
            id=new_id,
            title=src.title,
            author=src.author,
            dynasty=src.dynasty,
            genre=src.genre,
            content=src.content,
            analysis=src.analysis,
            tags=src.tags,
        )

    return poem


async def mimic_poem(req: GenerationRequest) -> Optional[Poem]:
    """仿写诗词"""
    if not req.draft:
        return None

    emotion = req.emotion or "思乡"
    style = req.style or "古风"
    images = req.images if req.images else ["明月"]

    user_prompt = (
        f"请仿写以下诗词/草稿：\n"
        f"原文：\n{req.draft}\n\n"
        f"仿写要求：\n"
        f"风格：{style}\n"
        f"情感基调：{emotion}\n"
    )
    if images:
        user_prompt += f"可融入意象：{'、'.join(images)}\n"

    try:
        raw = await _chat(MIMIC_SYSTEM, user_prompt)
        data = parse_llm_json(raw)
        poem = _build_poem_from_llm(data, style, images, 1, prefix="mimic")
    except Exception as e:
        logger.warning("LLM mimic failed: %s", e)
        # LLM 失败时回退
        poem = _fallback_poem(req.draft[:4], emotion, style, images, 1, prefix="mimic")

    return poem


def _build_poem_from_llm(data: dict, style: str, images: list, idx: int, prefix: str = "gen") -> Poem:
    """从 LLM 返回的 JSON 构建 Poem 对象"""
    poem_id = f"{prefix}-{int(time.time() * 1000)}-{idx}"
    content = data.get("content", [])
    if isinstance(content, str):
        content = [line.strip() for line in content.split("\n") if line.strip()]

    return Poem(
        id=poem_id,
        title=data.get("title", "无题"),
        author=Author(name="AI诗人", dynasty="现代", brief="AI 创作，仅供参考"),
        dynasty="现代",
        genre=data.get("genre", style),
        content=content,
        analysis=Analysis(
            translation=data.get("translation", ""),
            appreciation=data.get("appreciation", ""),
            cultural="AI 生成，仅供学习参考。",
        ),
        tags=list(images),
    )


def _fallback_poem(scene: str, emotion: str, style: str, images: list, idx: int, prefix: str = "gen") -> Poem:
    """LLM 不可用时的回退模板"""
    poem_id = f"{prefix}-{int(time.time() * 1000)}-{idx}"
    img = images[0] if images else "明月"
    return Poem(
        id=poem_id,
        title=f"{scene}寄意",
        author=Author(name="AI写手", dynasty="现代", brief="LLM 暂不可用，使用模板生成"),
        dynasty="现代",
        genre=style,
        content=[
            f"{scene}夜色凉如水",
            f"{img}清辉照九州",
            f"一缕{emotion}意",
            f"随风到远楼",
        ],
        analysis=Analysis(
            translation=f"在{scene}的夜晚，{img}的光辉洒满大地，一缕{emotion}之情随风飘向远方。",
            appreciation="LLM 服务暂不可用，此为模板生成，仅供参考。",
            cultural="AI 生成，仅供学习参考。",
        ),
        tags=list(images),
    )
