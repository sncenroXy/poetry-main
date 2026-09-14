"""
为所有诗词生成随机排序字段 sort_order

用法:
  python shuffle_poems.py              # 执行打散
  python shuffle_poems.py --preview    # 仅预览前 10 条
"""
import sys
import random
import pymongo
import argparse

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

sys.path.insert(0, __import__("os").path.dirname(__file__))
from app.config import settings

client = pymongo.MongoClient(settings.MONGODB_URI)
db = client[settings.DATABASE_NAME]
poems = db["poems"]


def shuffle():
    # 获取所有文档的 _id
    ids = [doc["_id"] for doc in poems.find({}, {"_id": 1})]
    total = len(ids)
    print(f"共 {total} 首诗词")

    # 生成随机顺序
    random.shuffle(ids)

    # 批量写入 sort_order
    ops = []
    for i, pid in enumerate(ids):
        ops.append(pymongo.UpdateOne(
            {"_id": pid},
            {"$set": {"sort_order": i}},
        ))
        if len(ops) >= 1000:
            poems.bulk_write(ops, ordered=False)
            print(f"  已处理 {i + 1}/{total}")
            ops = []

    if ops:
        poems.bulk_write(ops, ordered=False)

    print(f"完成！已为 {total} 首诗词生成随机排序")

    # 创建索引
    poems.create_index("sort_order")
    print("已创建 sort_order 索引")


def preview():
    print("当前前 10 条排序预览:")
    for doc in poems.find({}, {"_id": 1, "title": 1, "author.name": 1, "sort_order": 1}).sort("sort_order", 1).limit(10):
        order = doc.get("sort_order", "无")
        author = doc.get("author", {}).get("name", "")
        print(f"  [{order}] {doc['title']} — {author}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--preview", action="store_true")
    args = parser.parse_args()

    if args.preview:
        preview()
    else:
        shuffle()
        print()
        preview()
