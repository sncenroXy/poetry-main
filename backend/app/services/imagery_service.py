"""诗境漫游 — 意象分析服务"""
import logging
from app.models.request import ImageryAnalyzeRequest
from app.utils.llm import chat_json, parse_llm_json

logger = logging.getLogger(__name__)


IMAGERY_SYSTEM_PROMPT = """你是一位古典诗词意象分析专家。用户会给你一首诗词，你需要分析其中的核心意象并以 JSON 格式返回。

要求：
1. 提取 3-6 个核心意象节点（如月、霜、雁、柳等具象事物或意境）
2. 每个意象节点包含：
   - name: 意象名称（1-3字）
   - category: 分类（天象/地理/植物/动物/气象/人事/器物/情感）
   - significance: 该意象在本诗中的作用（一句话）
   - cultural_meaning: 该意象在中国古典文学中的文化含义与演变（200-300字）
   - related_poems: 包含同一意象的其他 2-3 首名篇，每首含 title/author/dynasty/quote
   - connections: 与本诗中其他意象的关联（名称列表）
3. 提供 poem_summary: 全诗概述（2-3句话）

严格按以下 JSON 格式返回，不要添加任何其他文字：
{
  "poem_summary": "...",
  "imagery_nodes": [
    {
      "name": "月",
      "category": "天象",
      "significance": "...",
      "cultural_meaning": "...",
      "related_poems": [
        {"title": "...", "author": "...", "dynasty": "...", "quote": "..."}
      ],
      "connections": ["霜", "乡"]
    }
  ]
}

注意：related_poems 必须是真实存在的诗词，不确定的请标注"(待核实)"。"""


async def analyze(req: ImageryAnalyzeRequest) -> dict:
    """分析诗词意象"""
    poem_desc = req.poem_text
    if req.title:
        poem_desc = f"《{req.title}》" + (f" — {req.author}" if req.author else "") + f"\n{req.poem_text}"

    try:
        user_msg = f"请分析以下诗词的意象：\n\n{poem_desc}"
        raw = await chat_json(IMAGERY_SYSTEM_PROMPT, user_msg, temperature=0.4, max_tokens=3000)
        data = parse_llm_json(raw)
        if not isinstance(data, dict) or "imagery_nodes" not in data or not isinstance(data["imagery_nodes"], list):
            raise ValueError("invalid response structure")
        return data

    except Exception as e:
        logger.warning("Imagery analysis failed: %s (%s)", e, type(e).__name__)
        return _fallback_analysis(req)


def _fallback_analysis(req: ImageryAnalyzeRequest) -> dict:
    """降级：返回基础分析框架"""
    return {
        "poem_summary": f"「{req.title or '此诗'}」意境深远，值得细细品味。（AI 分析暂时不可用）",
        "imagery_nodes": [
            {
                "name": "全诗",
                "category": "情感",
                "significance": "诗词整体意境",
                "cultural_meaning": "中国古典诗词讲究意境营造，通过具象事物表达抽象情感，形成独特的审美体验。建议您在 AI 恢复后重新分析。",
                "related_poems": [],
                "connections": [],
            }
        ],
        "fallback": True,
    }
