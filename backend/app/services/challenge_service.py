"""挑战服务 — 飞花令 & 答题闯关（含 AI 增强）"""
import json
import logging
import random
import uuid
from typing import List, Dict, Any, Optional
from openai import AsyncOpenAI
from app.config import settings
from app.database import poems_collection
from app.models import Poem
from app.utils.llm import parse_llm_json

logger = logging.getLogger(__name__)

# ---------- LLM 客户端（复用 LLM 配置） ----------

_client: Optional[AsyncOpenAI] = None


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.LLM_API_KEY,
            base_url=settings.LLM_BASE_URL,
        )
    return _client


async def _chat(system: str, user: str, temperature: float = 0.7) -> str:
    """调用 LLM 并返回文本"""
    client = _get_client()
    resp = await client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        max_tokens=2000,
    )
    result = (resp.choices[0].message.content or "").strip()
    logger.debug("Challenge LLM raw: %s", result[:500])
    return result


# ============================================================
#  原有功能（保留）
# ============================================================

async def _get_all_poems_content() -> List[Poem]:
    """获取所有诗词（仅用于接龙功能，不分页）"""
    poems = []
    cursor = poems_collection.find({}, {"_id": 1, "title": 1, "content": 1})
    async for doc in cursor:
        doc["id"] = doc.pop("_id", doc.get("id"))
        poems.append(Poem(
            id=doc["id"],
            title=doc.get("title", ""),
            content=doc.get("content", []),
        ))
    return poems


async def find_next_lines(line: str) -> List[Dict[str, str]]:
    """查找给定诗句的下句候选"""
    if not line or not line.strip():
        return []

    results = []
    poems = await _get_all_poems_content()

    for p in poems:
        content = p.content or []
        for i in range(len(content) - 1):
            if content[i] == line:
                results.append({
                    "poemId": p.id,
                    "title": p.title,
                    "next": content[i + 1]
                })
    return results


async def validate_chain(current: str, answer: str) -> bool:
    """验证接龙答案是否正确（精确匹配）"""
    if not current or not answer:
        return False

    poems = await _get_all_poems_content()
    for p in poems:
        content = p.content or []
        for i in range(len(content) - 1):
            if content[i] == current and content[i + 1] == answer:
                return True
    return False


async def generate_quiz(count: int = 3) -> List[Dict[str, Any]]:
    """生成填空选择题 — 使用 $sample 聚合随机抽取，避免全量加载"""
    sample_size = count * 3
    pipeline = [
        {"$sample": {"size": sample_size}},
        {"$project": {"_id": 0, "content": 1}},
    ]
    sampled_lines: List[str] = []
    async for doc in poems_collection.aggregate(pipeline):
        for line in (doc.get("content") or []):
            if len(line) >= 2:
                sampled_lines.append(line)

    if not sampled_lines:
        return []

    random.shuffle(sampled_lines)
    distractors = ["之", "人", "不", "天", "来", "春", "花", "梦", "风", "月"]

    questions = []
    for line in sampled_lines:
        if len(questions) >= count:
            break

        answer = line[-1]
        question = line[:-1] + "___"

        pool = [l[-1] for l in sampled_lines if l[-1] != answer]
        if len(pool) < 3:
            pool.extend(distractors)

        options = [answer]
        candidates = list(set(pool))
        random.shuffle(candidates)
        for c in candidates:
            if c not in options:
                options.append(c)
            if len(options) >= 4:
                break
        while len(options) < 4:
            d = random.choice(distractors)
            if d not in options:
                options.append(d)

        random.shuffle(options)
        answer_idx = options.index(answer)

        questions.append({
            "id": str(uuid.uuid4()),
            "question": question,
            "options": options,
            "answer": answer_idx,
            "type": "fill_blank",
            "explanation": "",
            "source": "",
        })

    return questions


# ============================================================
#  飞花令 AI 增强
# ============================================================

HINT_SYSTEM = """你是一位古典诗词教学助手。用户正在玩飞花令（诗词接龙），需要根据上句写出下句。
你需要根据提示级别给出不同程度的提示，帮助用户回忆而非直接告诉答案。

提示级别说明：
- level 1（意境提示）：描述这句诗所在诗篇的意境、情感氛围，让用户联想
- level 2（关键字提示）：给出下句中 2-3 个关键字（非连续），用"_"代替其他字
- level 3（首字提示）：直接给出下句的第一个字，并说明全句共几个字

返回 JSON 格式：
{
  "hint": "提示内容",
  "level": 1,
  "source_title": "出自哪首诗（如果知道）"
}

只返回 JSON，不要其他内容。"""


async def ai_hint(line: str, level: int = 1) -> Dict[str, Any]:
    """AI 渐进式提示"""
    user_msg = f"当前诗句：{line}\n请给出 level {level} 的提示。"
    try:
        raw = await _chat(HINT_SYSTEM, user_msg)
        return parse_llm_json(raw)
    except Exception as e:
        logger.warning("AI hint failed: %s", e)
        # fallback：尝试数据库查找
        next_lines = await find_next_lines(line)
        if next_lines:
            ans = next_lines[0]["next"]
            if level == 1:
                return {"hint": f"这首诗表达了一种深沉的情感，下句与此句意境相承。", "level": 1, "source_title": next_lines[0].get("title", "")}
            elif level == 2:
                masked = ans[0] + "_" * (len(ans) - 2) + ans[-1] if len(ans) >= 3 else "_" * len(ans)
                return {"hint": f"下句的结构是：{masked}", "level": 2, "source_title": next_lines[0].get("title", "")}
            else:
                return {"hint": f"下句的第一个字是「{ans[0]}」，全句共 {len(ans)} 个字。", "level": 3, "source_title": next_lines[0].get("title", "")}
        return {"hint": "暂时无法提供提示，请尝试其他诗句。", "level": level, "source_title": ""}


VALIDATE_SYSTEM = """你是一位古典诗词专家。用户正在玩飞花令（诗词接龙），给出了上句后写了一个下句。
请判断用户的回答是否正确（是否为该诗句的合理下句）。

判断标准：
1. 最佳情况：用户答案确实是原诗中紧接上句的下一句
2. 可接受：用户答案与标准答案仅有异体字、通假字差异（如"疑似"和"疑是"）
3. 不正确：答案明显不是该句的下句

返回 JSON 格式：
{
  "correct": true/false,
  "explanation": "解释说明（为什么对/错，引用原诗）",
  "correct_answer": "正确的下句",
  "source_title": "出自《xxx》",
  "source_author": "作者"
}

只返回 JSON，不要其他内容。"""


async def ai_validate_chain(current: str, answer: str) -> Dict[str, Any]:
    """AI 语义校验接龙答案"""
    # 快速通道：先走数据库精确匹配
    db_result = await validate_chain(current, answer)
    if db_result:
        # 精确匹配成功，直接返回，不浪费 LLM 调用
        next_lines = await find_next_lines(current)
        title = next_lines[0].get("title", "") if next_lines else ""
        return {
            "correct": True,
            "explanation": "回答正确！",
            "correct_answer": answer,
            "source_title": title,
            "source_author": "",
        }

    # 数据库未匹配，交给 AI 语义判断
    try:
        user_msg = f"上句：{current}\n用户回答：{answer}"
        raw = await _chat(VALIDATE_SYSTEM, user_msg)
        data = parse_llm_json(raw)
        return data
    except Exception as e:
        logger.warning("AI validate failed: %s", e)
        return {
            "correct": False,
            "explanation": "未能找到匹配的诗句，请检查后重试。",
            "correct_answer": "",
            "source_title": "",
            "source_author": "",
        }


CHAIN_TURN_SYSTEM = """你是一位精通古典诗词的AI诗人，正在和用户玩飞花令（诗词接龙）。
用户给出了一句诗，你需要：
1. 先回应这句诗的下一句（如果你知道原诗的话）
2. 然后给出一句新的诗句作为你的出题，让用户接下去

重要规则：
- 如果用户输入的不是诗句（比如"不知道"、"跳过"、"我不会"、"认输"等），你应该：
  - ai_answer 设为"没关系，我来出一道新题！"
  - 直接给出一个新题（new_line），不需要接句
  - comment 设为鼓励性的话
- 你回应的下句必须是真实存在的古典诗词，不要编造
- 你出的新题也必须是真实古典诗词中的某一句
- 适当变换朝代和作者，增加趣味性

返回 JSON 格式：
{
  "ai_answer": "你接的下句",
  "ai_answer_title": "下句出自《xxx》",
  "ai_answer_author": "作者",
  "new_line": "你出的新题（一句诗）",
  "new_line_title": "新题出自《xxx》",
  "new_line_author": "作者",
  "comment": "简短评语或趣味互动（20字以内）"
}

只返回 JSON，不要其他内容。"""


async def ai_chain_turn(current: str) -> Dict[str, Any]:
    """AI 对战：接句 + 出题"""
    try:
        user_msg = f"当前诗句：{current}\n请接出下句，并出一道新题。"
        raw = await _chat(CHAIN_TURN_SYSTEM, user_msg, temperature=0.8)
        return parse_llm_json(raw)
    except Exception as e:
        logger.warning("AI chain turn failed: %s", e)
        # fallback: 从数据库找下句，再随机出题
        next_lines = await find_next_lines(current)
        # 随机抽一句作为新题
        pipeline = [{"$sample": {"size": 1}}, {"$project": {"_id": 0, "title": 1, "content": 1, "author.name": 1}}]
        new_poem = None
        async for doc in poems_collection.aggregate(pipeline):
            new_poem = doc

        ai_ans = next_lines[0]["next"] if next_lines else "（AI 暂时接不上来）"
        ai_title = next_lines[0].get("title", "") if next_lines else ""

        new_line = ""
        new_title = ""
        new_author = ""
        if new_poem and new_poem.get("content"):
            lines = new_poem["content"]
            new_line = lines[random.randint(0, max(0, len(lines) - 2))] if lines else ""
            new_title = new_poem.get("title", "")
            new_author = (new_poem.get("author") or {}).get("name", "")

        return {
            "ai_answer": ai_ans,
            "ai_answer_title": ai_title,
            "ai_answer_author": "",
            "new_line": new_line,
            "new_line_title": new_title,
            "new_line_author": new_author,
            "comment": "让我来出一题！",
        }


# ============================================================
#  答题闯关 AI 增强
# ============================================================

AI_QUIZ_SYSTEM = """你是一位古典诗词出题专家。请根据要求生成诗词选择题。

题型包括（请随机混合出题）：
1. fill_blank（填空）：给出一句诗，挖掉其中 1-2 个字，让用户选择正确的字
2. next_line（上下句）：给出上句，选出正确的下句
3. author（作者识别）：给出一句/一首诗，选出正确的作者
4. sentiment（意境判断）：给出一句诗，判断其表达的情感/意境

要求：
1. 每道题必须基于真实存在的古典诗词，不要编造
2. 干扰选项要有迷惑性，不能一眼排除
3. 难度适中，覆盖唐宋名篇为主
4. 每道题附带简要解析

返回 JSON 数组格式：
[
  {
    "id": "唯一ID",
    "type": "fill_blank/next_line/author/sentiment",
    "question": "题目描述",
    "options": ["选项A", "选项B", "选项C", "选项D"],
    "answer": 0,
    "explanation": "解析（引用原诗，说明为什么选这个）",
    "source": "出自《xxx》- 作者"
  }
]

只返回 JSON 数组，不要其他内容。"""


async def ai_generate_quiz(count: int = 5) -> List[Dict[str, Any]]:
    """AI 生成多种题型的选择题"""
    try:
        user_msg = f"请生成 {count} 道诗词选择题，题型随机混合，难度适中。"
        raw = await _chat(AI_QUIZ_SYSTEM, user_msg, temperature=0.9)
        questions = parse_llm_json(raw)
        if isinstance(questions, list):
            # 确保每个题目有 id
            for i, q in enumerate(questions):
                if not q.get("id"):
                    q["id"] = str(uuid.uuid4())
            return questions
    except Exception as e:
        logger.warning("AI quiz generation failed: %s", e)

    # fallback: 使用数据库题目
    return await generate_quiz(count)


EXPLAIN_SYSTEM = """你是一位古典诗词教学专家。用户刚刚回答了一道诗词题，请为用户解析这道题。

要求：
1. 说明正确答案是什么，为什么是正确的
2. 如果用户答错了，解释用户选择为什么不对
3. 引用完整原诗（至少前四句）
4. 补充相关的诗词知识（如作者背景、写作背景、修辞手法等）
5. 语言亲切自然，像老师在讲课

返回 JSON 格式：
{
  "is_correct": true/false,
  "correct_option": "正确答案文本",
  "explanation": "详细解析",
  "full_poem": "完整原诗",
  "knowledge": "扩展知识点（50字以内）"
}

只返回 JSON，不要其他内容。"""


async def ai_explain_answer(question: Dict[str, Any], user_answer: int) -> Dict[str, Any]:
    """AI 解析单道题目"""
    correct_idx = question.get("answer", 0)
    is_correct = user_answer == correct_idx

    try:
        user_msg = (
            f"题目：{question.get('question', '')}\n"
            f"选项：{json.dumps(question.get('options', []), ensure_ascii=False)}\n"
            f"正确答案索引：{correct_idx}\n"
            f"用户选择索引：{user_answer}\n"
            f"用户{'回答正确' if is_correct else '回答错误'}"
        )
        if question.get("source"):
            user_msg += f"\n出处：{question['source']}"

        raw = await _chat(EXPLAIN_SYSTEM, user_msg)
        data = parse_llm_json(raw)
        data["is_correct"] = is_correct
        return data
    except Exception as e:
        logger.warning("AI explain failed: %s", e)
        options = question.get("options", [])
        return {
            "is_correct": is_correct,
            "correct_option": options[correct_idx] if correct_idx < len(options) else "",
            "explanation": f"正确答案是「{options[correct_idx]}」。" if correct_idx < len(options) else "解析暂不可用。",
            "full_poem": "",
            "knowledge": "",
        }


SUMMARY_SYSTEM = """你是一位古典诗词教学专家。用户刚刚完成了一轮诗词答题，请根据答题记录进行总结分析。

要求：
1. 给出总体评价（结合正确率）
2. 分析薄弱知识点（根据答错的题目类型和内容）
3. 推荐 2-3 首适合学习的诗词（针对薄弱点）
4. 给出鼓励性评语

返回 JSON 格式：
{
  "score_comment": "总体评价（如：表现优秀/良好/需要加油）",
  "weak_points": ["薄弱点1", "薄弱点2"],
  "recommendations": [
    {"title": "诗词标题", "author": "作者", "reason": "推荐理由"}
  ],
  "encouragement": "鼓励性评语（温暖、有文学气息）"
}

只返回 JSON，不要其他内容。"""


async def ai_quiz_summary(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """AI 答题总结分析"""
    total = len(results)
    correct = sum(1 for r in results if r.get("correct"))

    try:
        # 构造摘要传给 LLM
        summary_lines = [f"共 {total} 题，答对 {correct} 题。\n答题详情："]
        for i, r in enumerate(results):
            status = "✓" if r.get("correct") else "✗"
            q = r.get("question", "")
            source = r.get("source", "")
            q_type = r.get("type", "unknown")
            summary_lines.append(f"{i+1}. [{status}] ({q_type}) {q} | {source}")

        user_msg = "\n".join(summary_lines)
        raw = await _chat(SUMMARY_SYSTEM, user_msg)
        data = parse_llm_json(raw)
        data["total"] = total
        data["correct"] = correct
        return data
    except Exception as e:
        logger.warning("AI quiz summary failed: %s", e)
        rate = correct / total if total > 0 else 0
        if rate >= 0.8:
            comment = "表现优秀！"
        elif rate >= 0.6:
            comment = "表现良好，继续加油！"
        else:
            comment = "需要多加练习哦！"
        return {
            "total": total,
            "correct": correct,
            "score_comment": comment,
            "weak_points": [],
            "recommendations": [],
            "encouragement": "每一次练习都是进步，继续坚持！",
        }
