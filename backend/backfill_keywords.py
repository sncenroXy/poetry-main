"""
诗词检索关键词回填工具 — 为已导入的诗词补全 keywords 字段（jieba 分词倒排）

用法:
  python backfill_keywords.py           # 为所有缺失 keywords 的诗词补全
  python backfill_keywords.py --all     # 强制全部重建（含已有 keywords 的）
  python backfill_keywords.py --limit 100  # 仅处理前 100 首

说明: 新导入的数据已自动携带 keywords；本脚本用于老数据的一次性回填。
"""
import sys
import os
import argparse

import pymongo

# 确保能导入同目录的 app 包（可从任意目录运行）
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.config import settings
from app.utils.tokenizer import tokenize

# Windows 终端中文输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

client = pymongo.MongoClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]
poems = db["poems"]


def build_keywords(doc: dict) -> list:
    title = doc.get("title", "")
    author = (doc.get("author") or {}).get("name", "")
    content = doc.get("content") or []
    tags = doc.get("tags") or []
    text = " ".join([title, author, " ".join(content), " ".join(tags)])
    return tokenize(text)


def backfill(force: bool = False, limit: int = 0):
    query = {} if force else {"keywords": {"$exists": False}}
    total = poems.count_documents(query)
    print(f"待回填: {total} 首")

    cursor = poems.find(query, {"_id": 1, "title": 1, "author.name": 1, "content": 1, "tags": 1})
    if limit > 0:
        cursor = cursor.limit(limit)

    updated = 0
    for doc in cursor:
        keywords = build_keywords(doc)
        poems.update_one({"_id": doc["_id"]}, {"$set": {"keywords": keywords}})
        updated += 1
        if updated % 1000 == 0:
            print(f"  已处理 {updated}/{total if total else '?'} ...")

    print(f"完成: 更新 {updated} 首")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="回填诗词检索关键词")
    parser.add_argument("--all", action="store_true", help="强制重建所有诗词的关键词")
    parser.add_argument("--limit", type=int, default=0, help="限制处理数量")
    args = parser.parse_args()

    backfill(force=args.all, limit=args.limit)
