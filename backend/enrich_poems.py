"""
诗词数据补全工具 — 批量为数据库中的诗词补全 author.brief 和 analysis 字段

使用 LLM（OpenAI 兼容接口）并发 + 批量补全，大幅提速。

用法:
  python enrich_poems.py brief                       # 补全作者简介
  python enrich_poems.py analysis                    # 补全诗词赏析
  python enrich_poems.py all                         # 补全全部
  python enrich_poems.py stats                       # 查看缺失统计
  python enrich_poems.py analysis --concurrency 20   # 设置并发数（默认 10）
  python enrich_poems.py analysis --batch-size 5     # 每次 LLM 调用处理几首（默认 5）
  python enrich_poems.py brief --limit 100           # 限制处理数量
  python enrich_poems.py brief --dry-run             # 仅预览，不写入

提速原理:
  - 并发: 同时发出 N 个 LLM 请求（默认 10 路并发）
  - 批量: 一次 prompt 让 LLM 同时赏析多首诗词（默认 5 首/次）
  - 10 并发 x 5 批量 = 50 倍吞吐量提升
"""
import sys
import os
import json
import asyncio
import argparse
import time
import logging
from typing import List, Dict, Any

# Windows 终端中文输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, os.path.dirname(__file__))

from openai import AsyncOpenAI
from app.config import settings

import pymongo

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

client_mongo = pymongo.MongoClient(settings.MONGODB_URI)
db = client_mongo[settings.DATABASE_NAME]
poems = db["poems"]


def get_llm_client() -> AsyncOpenAI:
    return AsyncOpenAI(
        api_key=settings.LLM_API_KEY,
        base_url=settings.LLM_BASE_URL,
    )


def parse_json_safe(raw: str):
    """从 LLM 返回文本中提取 JSON（支持对象和数组）"""
    text = raw.strip()
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    text = text.strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 尝试找 [ ] 或 { } 边界
        for open_ch, close_ch in [("[", "]"), ("{", "}")]:
            start = text.find(open_ch)
            end = text.rfind(close_ch)
            if start != -1 and end > start:
                try:
                    return json.loads(text[start:end + 1])
                except json.JSONDecodeError:
                    continue
    return {}


# ========== 作者简介补全（并发） ==========

BRIEF_SYSTEM = """你是一位中国古典文学专家。请为以下诗人/词人提供简洁的介绍。

要求：
1. 包含字号、朝代、文学地位、代表作品风格
2. 控制在 50-80 字以内
3. 返回 JSON 格式：{"brief": "简介内容"}
4. 只返回 JSON，不要其他内容"""


async def _enrich_one_author(
    sem: asyncio.Semaphore,
    llm: AsyncOpenAI,
    author: dict,
    index: int,
    total: int,
) -> bool:
    """并发处理单个作者"""
    name = author["_id"]
    dynasty = author.get("dynasty", "")

    async with sem:
        try:
            user_msg = f"诗人：{name}"
            if dynasty:
                user_msg += f"，朝代：{dynasty}"

            resp = await llm.chat.completions.create(
                model=settings.LLM_MODEL,
                messages=[
                    {"role": "system", "content": BRIEF_SYSTEM},
                    {"role": "user", "content": user_msg},
                ],
                temperature=0.3,
                max_tokens=200,
            )
            raw = (resp.choices[0].message.content or "").strip()
            data = parse_json_safe(raw)
            brief = data.get("brief", "") if isinstance(data, dict) else ""

            if brief:
                result = poems.update_many(
                    {"author.name": name, "$or": [
                        {"author.brief": {"$exists": False}},
                        {"author.brief": ""},
                        {"author.brief": None},
                    ]},
                    {"$set": {"author.brief": brief}},
                )
                logger.info("[%d/%d] %s (%s) -> %d首已更新: %s",
                            index, total, name, dynasty, result.modified_count, brief[:50])
                return True
            else:
                logger.warning("[%d/%d] %s -> LLM 返回为空", index, total, name)
                return False
        except Exception as e:
            logger.error("[%d/%d] %s -> 失败: %s", index, total, name, e)
            return False


async def enrich_author_briefs(llm: AsyncOpenAI, limit: int = 0, dry_run: bool = False, concurrency: int = 10):
    """并发补全作者简介"""
    pipeline = [
        {"$match": {"$or": [
            {"author.brief": {"$exists": False}},
            {"author.brief": ""},
            {"author.brief": None},
        ]}},
        {"$group": {
            "_id": "$author.name",
            "dynasty": {"$first": "$author.dynasty"},
            "count": {"$sum": 1},
        }},
        {"$sort": {"count": -1}},
    ]
    authors = list(poems.aggregate(pipeline))
    # 过滤掉 AI / 佚名
    authors = [a for a in authors if a["_id"] and a["_id"] not in ("AI诗人", "AI润色", "AI写手", "佚名")]

    if limit > 0:
        authors = authors[:limit]

    total = len(authors)
    logger.info("需补全作者简介: %d 位作者, 并发数: %d", total, concurrency)

    if not authors:
        logger.info("所有作者简介已完整")
        return

    if dry_run:
        for i, a in enumerate(authors):
            logger.info("[预览 %d/%d] %s (%s) — %d 首", i+1, total, a["_id"], a.get("dynasty",""), a["count"])
        return

    sem = asyncio.Semaphore(concurrency)
    tasks = [
        _enrich_one_author(sem, llm, author, i + 1, total)
        for i, author in enumerate(authors)
    ]
    results = await asyncio.gather(*tasks)
    success = sum(1 for r in results if r)
    failed = total - success
    logger.info("作者简介补全完成: 成功 %d, 失败 %d", success, failed)


# ========== 诗词赏析补全（并发 + 批量） ==========

ANALYSIS_BATCH_SYSTEM = """你是一位中国古典诗词赏析专家。请为以下多首诗词分别提供赏析信息。

每首诗词需要：
1. translation（白话译文）：逐句翻译，80-150 字
2. appreciation（赏析）：分析意境、手法、情感，80-150 字
3. cultural（文化拓展）：历史典故、文化背景，50-100 字

返回 JSON 数组，每个元素对应一首诗词，按输入顺序排列：
[
  {"id": "诗词ID", "translation": "...", "appreciation": "...", "cultural": "..."},
  ...
]

只返回 JSON 数组，不要其他内容。"""

# 单首模式的 system prompt（当 batch_size=1 时使用）
ANALYSIS_SINGLE_SYSTEM = """你是一位中国古典诗词赏析专家。请为以下诗词提供赏析信息。

要求：
1. translation（白话译文）：逐句翻译为通俗易懂的现代汉语，80-150 字
2. appreciation（赏析）：分析诗词的意境、手法、情感，80-150 字
3. cultural（文化拓展）：补充相关历史典故、文化背景，50-100 字

返回 JSON 格式：
{
  "translation": "白话译文",
  "appreciation": "赏析内容",
  "cultural": "文化拓展"
}

只返回 JSON，不要其他内容。"""


async def _enrich_analysis_batch(
    sem: asyncio.Semaphore,
    llm: AsyncOpenAI,
    batch: List[dict],
    batch_index: int,
    total_batches: int,
) -> int:
    """并发处理一批诗词赏析"""
    async with sem:
        try:
            if len(batch) == 1:
                # 单首模式
                doc = batch[0]
                content_text = "\n".join(doc["content"]) if isinstance(doc["content"], list) else str(doc["content"])
                user_msg = (
                    f"标题：{doc['title']}\n"
                    f"作者：{doc.get('author', {}).get('name', '佚名')}\n"
                    f"朝代：{doc.get('dynasty', '')}\n"
                    f"原文：\n{content_text}"
                )
                resp = await llm.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": ANALYSIS_SINGLE_SYSTEM},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.3,
                    max_tokens=800,
                )
                raw = (resp.choices[0].message.content or "").strip()
                data = parse_json_safe(raw)
                if isinstance(data, dict) and (data.get("translation") or data.get("appreciation")):
                    poems.update_one(
                        {"_id": doc["_id"]},
                        {"$set": {
                            "analysis.translation": data.get("translation", ""),
                            "analysis.appreciation": data.get("appreciation", ""),
                            "analysis.cultural": data.get("cultural", ""),
                        }},
                    )
                    logger.info("[批次 %d/%d] %s -> 已更新", batch_index, total_batches, doc["title"])
                    return 1
                else:
                    logger.warning("[批次 %d/%d] %s -> LLM 返回为空", batch_index, total_batches, doc["title"])
                    return 0
            else:
                # 批量模式
                lines = []
                for idx, doc in enumerate(batch):
                    content_text = "\n".join(doc["content"]) if isinstance(doc["content"], list) else str(doc["content"])
                    lines.append(
                        f"--- 第{idx+1}首 (id: {doc['_id']}) ---\n"
                        f"标题：{doc['title']}\n"
                        f"作者：{doc.get('author', {}).get('name', '佚名')}\n"
                        f"朝代：{doc.get('dynasty', '')}\n"
                        f"原文：\n{content_text}\n"
                    )
                user_msg = "\n".join(lines)

                resp = await llm.chat.completions.create(
                    model=settings.LLM_MODEL,
                    messages=[
                        {"role": "system", "content": ANALYSIS_BATCH_SYSTEM},
                        {"role": "user", "content": user_msg},
                    ],
                    temperature=0.3,
                    max_tokens=800 * len(batch),
                )
                raw = (resp.choices[0].message.content or "").strip()
                results = parse_json_safe(raw)

                if not isinstance(results, list):
                    # LLM 可能返回了单个对象而不是数组
                    if isinstance(results, dict):
                        results = [results]
                    else:
                        logger.warning("[批次 %d/%d] LLM 返回格式异常", batch_index, total_batches)
                        return 0

                updated = 0
                for item in results:
                    if not isinstance(item, dict):
                        continue
                    # 尝试匹配 ID
                    item_id = item.get("id", "")
                    translation = item.get("translation", "")
                    appreciation = item.get("appreciation", "")
                    cultural = item.get("cultural", "")

                    if not (translation or appreciation):
                        continue

                    if item_id:
                        # 按 ID 精确更新
                        poems.update_one(
                            {"_id": item_id},
                            {"$set": {
                                "analysis.translation": translation,
                                "analysis.appreciation": appreciation,
                                "analysis.cultural": cultural,
                            }},
                        )
                        updated += 1
                    else:
                        # 无 ID 时按顺序匹配
                        idx_in_batch = results.index(item)
                        if idx_in_batch < len(batch):
                            poems.update_one(
                                {"_id": batch[idx_in_batch]["_id"]},
                                {"$set": {
                                    "analysis.translation": translation,
                                    "analysis.appreciation": appreciation,
                                    "analysis.cultural": cultural,
                                }},
                            )
                            updated += 1

                titles = ", ".join(d["title"] for d in batch[:3])
                if len(batch) > 3:
                    titles += "..."
                logger.info("[批次 %d/%d] %s -> 更新 %d/%d 首",
                            batch_index, total_batches, titles, updated, len(batch))
                return updated

        except Exception as e:
            titles = ", ".join(d["title"] for d in batch[:2])
            logger.error("[批次 %d/%d] %s... -> 失败: %s", batch_index, total_batches, titles, e)
            return 0


async def enrich_analysis(
    llm: AsyncOpenAI,
    limit: int = 0,
    dry_run: bool = False,
    concurrency: int = 10,
    batch_size: int = 5,
):
    """并发 + 批量补全诗词赏析"""
    query = {"$or": [
        {"analysis": {"$exists": False}},
        {"analysis": {}},
        {"analysis": None},
        {"analysis.translation": {"$exists": False}},
        {"analysis.translation": ""},
        {"analysis.translation": None},
    ]}
    query["_id"] = {"$not": {"$regex": "^(gen-|mimic-|vision-|.*-opt-)"}}

    total = poems.count_documents(query)
    logger.info("需补全赏析: %d 首, 并发数: %d, 批大小: %d", total, concurrency, batch_size)

    if total == 0:
        logger.info("所有诗词赏析已完整")
        return

    cursor = poems.find(
        query,
        {"_id": 1, "title": 1, "author.name": 1, "dynasty": 1, "genre": 1, "content": 1}
    )
    if limit > 0:
        cursor = cursor.limit(limit)

    all_docs = list(cursor)
    logger.info("实际待处理: %d 首", len(all_docs))

    if dry_run:
        for i, doc in enumerate(all_docs[:20]):
            logger.info("[预览 %d] %s — %s", i+1, doc["title"], doc.get("author", {}).get("name", ""))
        if len(all_docs) > 20:
            logger.info("... 还有 %d 首", len(all_docs) - 20)
        return

    # 分批
    batches = []
    for i in range(0, len(all_docs), batch_size):
        batches.append(all_docs[i:i + batch_size])

    total_batches = len(batches)
    logger.info("共 %d 个批次, 预计 LLM 调用 %d 次", total_batches, total_batches)

    sem = asyncio.Semaphore(concurrency)
    tasks = [
        _enrich_analysis_batch(sem, llm, batch, i + 1, total_batches)
        for i, batch in enumerate(batches)
    ]

    start_time = time.time()
    results = await asyncio.gather(*tasks)
    elapsed = time.time() - start_time

    success = sum(results)
    logger.info("赏析补全完成: 成功 %d/%d 首, 耗时 %.1f 秒 (%.1f 首/秒)",
                success, len(all_docs), elapsed, success / elapsed if elapsed > 0 else 0)


# ========== 统计 ==========

def show_stats():
    """显示数据库字段完整性统计"""
    total = poems.count_documents({})

    real_query = {"_id": {"$not": {"$regex": "^(gen-|mimic-|vision-|.*-opt-)"}}}
    real_total = poems.count_documents(real_query)

    no_brief = poems.count_documents({
        **real_query,
        "$or": [
            {"author.brief": {"$exists": False}},
            {"author.brief": ""},
            {"author.brief": None},
        ]
    })

    no_analysis = poems.count_documents({
        **real_query,
        "$or": [
            {"analysis": {"$exists": False}},
            {"analysis": {}},
            {"analysis": None},
            {"analysis.translation": {"$exists": False}},
            {"analysis.translation": ""},
            {"analysis.translation": None},
        ]
    })

    print(f"\n{'='*50}")
    print(f"数据库字段完整性统计")
    print(f"{'='*50}")
    print(f"总计: {total} 首 (其中真实诗词 {real_total} 首)")
    print(f"")
    print(f"作者简介 (author.brief):")
    print(f"  已有: {real_total - no_brief} 首")
    print(f"  缺失: {no_brief} 首 ({no_brief/real_total*100:.1f}%)" if real_total else "  缺失: 0")
    print(f"")
    print(f"诗词赏析 (analysis):")
    print(f"  已有: {real_total - no_analysis} 首")
    print(f"  缺失: {no_analysis} 首 ({no_analysis/real_total*100:.1f}%)" if real_total else "  缺失: 0")
    print(f"")

    pipeline = [
        {"$match": {
            **real_query,
            "$or": [
                {"author.brief": {"$exists": False}},
                {"author.brief": ""},
                {"author.brief": None},
            ]
        }},
        {"$group": {"_id": "$author.name"}},
        {"$count": "total"},
    ]
    author_calls = list(poems.aggregate(pipeline))
    author_count = author_calls[0]["total"] if author_calls else 0

    batch_calls = (no_analysis + 4) // 5  # 默认 batch_size=5

    print(f"预估 LLM 调用次数:")
    print(f"  作者简介: ~{author_count} 次 (按作者去重)")
    print(f"  诗词赏析: ~{batch_calls} 次 (每次 5 首, 共 {no_analysis} 首)")
    print(f"  合计: ~{author_count + batch_calls} 次")
    print(f"")
    print(f"提速参数参考 (默认 --concurrency 10 --batch-size 5):")
    print(f"  串行逐首: {no_analysis} 次调用")
    print(f"  当前方案: {batch_calls} 次调用 x 10 并发 ≈ {(batch_calls + 9)//10} 轮")


async def main():
    parser = argparse.ArgumentParser(description="诗词数据补全工具（并发+批量提速版）")
    parser.add_argument("action", choices=["brief", "analysis", "all", "stats"],
                        help="brief=作者简介, analysis=赏析, all=全部, stats=统计")
    parser.add_argument("--limit", type=int, default=0,
                        help="限制处理数量（0=不限制）")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅预览，不写入数据库")
    parser.add_argument("--concurrency", "-c", type=int, default=10,
                        help="并发数（默认 10）")
    parser.add_argument("--batch-size", "-b", type=int, default=5,
                        help="每次 LLM 调用处理几首诗（默认 5，仅 analysis 有效）")

    args = parser.parse_args()

    if args.action == "stats":
        show_stats()
        return

    if not settings.LLM_API_KEY:
        print("错误: 未配置 LLM_API_KEY，请在 backend/.env 中设置")
        sys.exit(1)

    llm = get_llm_client()

    if args.action in ("brief", "all"):
        await enrich_author_briefs(llm, limit=args.limit, dry_run=args.dry_run, concurrency=args.concurrency)

    if args.action in ("analysis", "all"):
        await enrich_analysis(llm, limit=args.limit, dry_run=args.dry_run,
                              concurrency=args.concurrency, batch_size=args.batch_size)


if __name__ == "__main__":
    asyncio.run(main())
