"""AI 诗词助手服务 — 基于 OpenAI 兼容 API"""
import logging
from typing import Optional, List, Dict
from openai import AsyncOpenAI
from app.config import settings
from app.models.request import AssistantChatRequest

logger = logging.getLogger(__name__)

_client: Optional[AsyncOpenAI] = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
    return _client


ASSISTANT_SYSTEM_PROMPT = """你是「诗词雅韵」平台的 AI 诗词助手，一位博学多才的古典文学导师。你精通中国古典诗词的方方面面，能够为用户提供深入、详尽的讲解与指导。

你的能力范围：
1. **诗词赏析**：逐句解读诗词的意境、修辞手法、情感表达，帮助用户真正读懂每一首诗。
2. **典故解说**：讲解诗词中涉及的历史典故、文化背景，让用户知其然更知其所以然。
3. **格律知识**：解释平仄、押韵、对仗等格律规则，辅导用户理解和创作格律诗词。
4. **名句出处**：帮助用户查找名句的出处、作者及创作背景。
5. **诗人生平**：介绍诗人的生平事迹、创作风格、代表作品及其文学地位。
6. **意境分析**：深入剖析诗词所营造的意境、象征含义及审美特色。

回答要求：
- 回答详细充实，通常在 300-500 字左右，确保用户能学到东西
- 引用原诗原句时用「」标注
- 涉及专业术语时给出通俗解释
- 适当延伸相关知识，帮助用户建立知识网络
- 语言风格：温文尔雅，既有学术深度又平易近人
- 如果用户的问题不在以上范围，友好地引导回诗词相关话题"""

MAX_HISTORY_ROUNDS = 10


def _build_messages(req: AssistantChatRequest) -> List[Dict[str, str]]:
    """构造对话消息列表：system + 历史 + 当前用户消息"""
    messages = [{"role": "system", "content": ASSISTANT_SYSTEM_PROMPT}]

    # 限制历史轮数，取最近的 MAX_HISTORY_ROUNDS 条
    history = req.history[-MAX_HISTORY_ROUNDS * 2:] if req.history else []
    for msg in history:
        messages.append({"role": msg.role, "content": msg.content})

    messages.append({"role": "user", "content": req.message})
    return messages


async def chat(req: AssistantChatRequest) -> dict:
    """AI 助手对话入口"""
    try:
        client = _get_client()
        messages = _build_messages(req)

        resp = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2000,
        )
        reply = (resp.choices[0].message.content or "").strip()
        if not reply:
            reply = "抱歉，我暂时无法回答这个问题，请稍后再试。"

        return {"reply": reply}

    except Exception as e:
        logger.warning("AI assistant chat failed: %s", e)
        return {
            "reply": _fallback_reply(req.message),
            "fallback": True,
        }


def _fallback_reply(message: str) -> str:
    """LLM 不可用时的降级回复"""
    if any(kw in message for kw in ["平仄", "格律", "押韵", "对仗"]):
        return (
            "关于格律知识：中国古典诗词讲究平仄、押韵与对仗。"
            "平声（阴平、阳平）与仄声（上声、去声、入声）交替排列，"
            "形成抑扬顿挫的节奏美。建议您查阅王力先生的《诗词格律》一书，"
            "系统学习格律知识。\n\n"
            "（AI 服务暂时不可用，以上为预设回复，恢复后将为您提供更详细的解答。）"
        )
    if any(kw in message for kw in ["李白", "杜甫", "白居易", "苏轼", "辛弃疾"]):
        return (
            "这位诗人是中国文学史上的重要人物，留下了大量脍炙人口的诗篇。"
            "建议您在诗词库中搜索该诗人的作品，细细品读。\n\n"
            "（AI 服务暂时不可用，以上为预设回复，恢复后将为您提供更详细的解答。）"
        )
    return (
        "感谢您的提问！诗词世界博大精深，每一首诗都承载着诗人的情感与智慧。"
        "建议您先在诗词库中探索感兴趣的作品，也可以尝试飞花令和答题闯关来加深学习。\n\n"
        "（AI 服务暂时不可用，以上为预设回复，恢复后将为您提供更详细的解答。）"
    )
