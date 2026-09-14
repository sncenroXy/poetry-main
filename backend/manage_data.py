"""
诗词数据管理工具
用法:
  python manage_data.py list              # 查看所有诗词
  python manage_data.py add               # 交互式添加一首诗词
  python manage_data.py import data.json  # 从 JSON 文件批量导入
  python manage_data.py delete <id>       # 删除指定诗词
  python manage_data.py clear             # 清空所有数据
"""
import sys
import json
import pymongo

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["poetrydb"]
poems = db["poems"]


def list_poems():
    count = poems.count_documents({})
    print(f"\n共 {count} 首诗词\n{'='*50}")
    for doc in poems.find():
        author = doc.get("author", {})
        content = doc.get("content", [])
        print(f"  ID: {doc['_id']}")
        print(f"  标题: {doc.get('title', '无题')}")
        print(f"  作者: {author.get('name', '未知')} ({author.get('dynasty', '')})")
        print(f"  内容: {'，'.join(content[:2])}…" if len(content) > 2 else f"  内容: {'，'.join(content)}")
        print(f"  标签: {', '.join(doc.get('tags', []))}")
        print("-" * 50)


def add_poem():
    print("\n=== 添加诗词 ===")
    pid = input("ID (如 poem-4): ").strip()
    title = input("标题: ").strip()
    author_name = input("作者: ").strip()
    dynasty = input("朝代: ").strip()
    author_brief = input("作者简介: ").strip()
    genre = input("体裁 (如 五言绝句): ").strip()
    print("输入诗词内容，每行一句，输入空行结束:")
    content = []
    while True:
        line = input("  > ").strip()
        if not line:
            break
        content.append(line)
    translation = input("白话译文: ").strip()
    appreciation = input("赏析: ").strip()
    cultural = input("文化拓展: ").strip()
    tags_input = input("标签 (逗号分隔): ").strip()
    tags = [t.strip() for t in tags_input.split(",") if t.strip()]

    doc = {
        "_id": pid,
        "title": title,
        "author": {"name": author_name, "dynasty": dynasty, "brief": author_brief},
        "dynasty": dynasty,
        "genre": genre,
        "content": content,
        "analysis": {
            "translation": translation,
            "appreciation": appreciation,
            "cultural": cultural,
        },
        "tags": tags,
    }

    poems.update_one({"_id": pid}, {"$set": doc}, upsert=True)
    print(f"\n已添加: {title}")


def import_poems(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    items = data if isinstance(data, list) else data.get("poems", [data])
    count = 0
    for item in items:
        if "id" in item and "_id" not in item:
            item["_id"] = item.pop("id")
        if "_id" not in item:
            print(f"  跳过 (无 id): {item.get('title', '?')}")
            continue
        poems.update_one({"_id": item["_id"]}, {"$set": item}, upsert=True)
        print(f"  导入: {item.get('title', item['_id'])}")
        count += 1

    print(f"\n共导入 {count} 首诗词")


def delete_poem(pid):
    result = poems.delete_one({"_id": pid})
    if result.deleted_count:
        print(f"已删除: {pid}")
    else:
        print(f"未找到: {pid}")


def clear_all():
    confirm = input("确认清空所有诗词数据? (yes/no): ").strip()
    if confirm == "yes":
        result = poems.delete_many({})
        print(f"已删除 {result.deleted_count} 条数据")
    else:
        print("已取消")


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] == "list":
        list_poems()
    elif args[0] == "add":
        add_poem()
    elif args[0] == "import" and len(args) > 1:
        import_poems(args[1])
    elif args[0] == "delete" and len(args) > 1:
        delete_poem(args[1])
    elif args[0] == "clear":
        clear_all()
    else:
        print(__doc__)
