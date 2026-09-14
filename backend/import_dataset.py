"""
古诗词数据集批量导入工具
从 chinese-poetry/chinese-poetry 数据集导入唐诗、宋词到 MongoDB

用法:
  python import_dataset.py tang <file1.json> [file2.json ...]   # 导入唐诗
  python import_dataset.py ci <file1.json> [file2.json ...]     # 导入宋词
  python import_dataset.py auto <dir>                            # 自动扫描目录导入
  python import_dataset.py stats                                 # 查看统计信息
"""
import sys
import os
import json
import hashlib
import pymongo

# Windows 终端中文输出
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

client = pymongo.MongoClient("mongodb://localhost:27017")
db = client["poetrydb"]
poems = db["poems"]

# 朝代映射
DYNASTY_MAP = {
    "tang": "唐",
    "ci": "宋",
    "song": "宋",
}

# 常见唐代诗人简介
AUTHOR_BRIEFS = {
    "李白": "唐代伟大的浪漫主义诗人，字太白，号青莲居士，被后人誉为「诗仙」。",
    "杜甫": "唐代伟大的现实主义诗人，字子美，自号少陵野老，被后人尊称为「诗圣」。",
    "王维": "唐代诗人、画家，字摩诘，号摩诘居士，有「诗佛」之称。",
    "白居易": "唐代诗人，字乐天，号香山居士，诗风平易通俗。",
    "李商隐": "唐代诗人，字义山，号玉谿生，擅长骈文与律诗。",
    "杜牧": "唐代诗人，字牧之，号樊川居士，与李商隐并称「小李杜」。",
    "王昌龄": "唐代诗人，字少伯，有「七绝圣手」之称。",
    "孟浩然": "唐代山水田园诗人，字浩然，世称「孟襄阳」。",
    "韩愈": "唐代文学家、思想家，字退之，世称「韩昌黎」，唐宋八大家之首。",
    "柳宗元": "唐代文学家、思想家，字子厚，世称「柳河东」。",
    "刘禹锡": "唐代诗人，字梦得，有「诗豪」之称。",
    "岑参": "唐代诗人，边塞诗人代表，与高适并称「高岑」。",
    "高适": "唐代诗人，字达夫，边塞诗派重要代表。",
    "温庭筠": "唐代诗人、词人，字飞卿，花间派代表词人。",
    "贾岛": "唐代诗人，字阆仙，以苦吟著称。",
    "元稹": "唐代诗人，字微之，与白居易并称「元白」。",
    "李贺": "唐代诗人，字长吉，后世称为「诗鬼」。",
    "王勃": "唐代诗人，字子安，初唐四杰之首。",
    "骆宾王": "唐代诗人，字观光，初唐四杰之一。",
    "陈子昂": "唐代诗人，字伯玉，唐诗革新先驱。",
    "苏轼": "北宋文学家，字子瞻，号东坡居士，豪放派代表词人。",
    "辛弃疾": "南宋词人，字幼安，号稼轩，豪放派代表。",
    "李清照": "宋代女词人，号易安居士，婉约派代表。",
    "柳永": "北宋词人，字耆卿，婉约派代表。",
    "欧阳修": "北宋文学家，字永叔，号醉翁、六一居士。",
    "晏殊": "北宋词人，字同叔，擅长小令。",
    "周邦彦": "北宋词人，字美成，号清真居士，婉约派集大成者。",
    "秦观": "北宋词人，字少游，号淮海居士。",
    "姜夔": "南宋词人，字尧章，号白石道人。",
    "陆游": "南宋诗人，字务观，号放翁。",
    "范仲淹": "北宋政治家、文学家，字希文。",
    "王安石": "北宋政治家、文学家，字介甫，号半山。",
    "贺铸": "北宋词人，字方回，号庆湖遗老。",
    "吴文英": "南宋词人，字君特，号梦窗。",
    "纳兰性德": "清代词人，字容若，号楞伽山人。",
}


def generate_id(dtype, title, author):
    """生成稳定的唯一 ID"""
    raw = f"{dtype}-{author}-{title}"
    h = hashlib.md5(raw.encode("utf-8")).hexdigest()[:8]
    return f"{dtype}-{h}"


def detect_genre(content_lines):
    """根据句式初步判断体裁"""
    if not content_lines:
        return None
    first = content_lines[0].replace("，", "").replace("。", "").replace("！", "").replace("？", "")
    clen = len(first)
    total = len(content_lines)
    if clen <= 5 and total == 4:
        return "五言绝句"
    elif clen <= 5 and total == 8:
        return "五言律诗"
    elif clen <= 7 and total == 4:
        return "七言绝句"
    elif clen <= 7 and total == 8:
        return "七言律诗"
    return None


def convert_tang_poem(item):
    """转换唐诗格式到项目 Poem 模型"""
    author_name = item.get("author", "佚名")
    title = item.get("title", "无题")
    paragraphs = item.get("paragraphs", [])

    pid = generate_id("tang", title, author_name)
    genre = detect_genre(paragraphs)

    doc = {
        "_id": pid,
        "title": title,
        "author": {
            "name": author_name,
            "dynasty": "唐",
            "brief": AUTHOR_BRIEFS.get(author_name, ""),
        },
        "dynasty": "唐",
        "genre": genre,
        "content": paragraphs,
        "tags": ["唐诗"],
        "analysis": {},
    }

    if genre:
        doc["tags"].append(genre)

    return doc


def convert_ci(item):
    """转换宋词格式到项目 Poem 模型"""
    author_name = item.get("author", "佚名")
    rhythmic = item.get("rhythmic", "无题")  # 词牌名作为标题
    paragraphs = item.get("paragraphs", [])

    pid = generate_id("ci", rhythmic, author_name)

    doc = {
        "_id": pid,
        "title": rhythmic,
        "author": {
            "name": author_name,
            "dynasty": "宋",
            "brief": AUTHOR_BRIEFS.get(author_name, ""),
        },
        "dynasty": "宋",
        "genre": "词",
        "content": paragraphs,
        "tags": ["宋词", rhythmic],
        "analysis": {},
    }

    return doc


def import_file(filepath, dtype):
    """导入单个 JSON 文件"""
    converter = convert_tang_poem if dtype == "tang" else convert_ci

    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        data = [data]

    count = 0
    skipped = 0
    for item in data:
        try:
            doc = converter(item)
            poems.update_one({"_id": doc["_id"]}, {"$set": doc}, upsert=True)
            count += 1
        except Exception as e:
            skipped += 1
            if skipped <= 3:
                print(f"  [跳过] {e}")

    return count, skipped


def import_files(dtype, filepaths):
    """批量导入多个文件"""
    total = 0
    total_skipped = 0
    for fp in filepaths:
        if not os.path.exists(fp):
            print(f"  [文件不存在] {fp}")
            continue
        print(f"  导入: {os.path.basename(fp)} ...", end=" ")
        count, skipped = import_file(fp, dtype)
        print(f"{count} 首" + (f" (跳过 {skipped})" if skipped else ""))
        total += count
        total_skipped += skipped

    print(f"\n{'='*40}")
    print(f"总计导入: {total} 首" + (f"  跳过: {total_skipped}" if total_skipped else ""))


def auto_import(directory):
    """自动扫描目录并导入"""
    if not os.path.isdir(directory):
        print(f"目录不存在: {directory}")
        return

    tang_files = []
    ci_files = []

    for fname in sorted(os.listdir(directory)):
        fpath = os.path.join(directory, fname)
        if not fname.endswith(".json"):
            continue
        # 根据文件名判断类型
        lower = fname.lower()
        if "tang" in lower or "poet" in lower or "唐" in lower:
            tang_files.append(fpath)
        elif "ci" in lower or "词" in lower:
            ci_files.append(fpath)

    if tang_files:
        print(f"\n--- 唐诗 ({len(tang_files)} 个文件) ---")
        import_files("tang", tang_files)

    if ci_files:
        print(f"\n--- 宋词 ({len(ci_files)} 个文件) ---")
        import_files("ci", ci_files)

    if not tang_files and not ci_files:
        print("未发现可识别的数据文件。文件名需包含 tang/poet/唐 或 ci/词")


def show_stats():
    """显示数据库统计信息"""
    total = poems.count_documents({})
    print(f"\n数据库统计")
    print(f"{'='*40}")
    print(f"总计: {total} 首\n")

    # 按朝代统计
    pipeline = [
        {"$group": {"_id": "$dynasty", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    print("按朝代:")
    for doc in poems.aggregate(pipeline):
        dynasty = doc["_id"] or "未知"
        print(f"  {dynasty}: {doc['count']} 首")

    # 按体裁统计
    pipeline = [
        {"$group": {"_id": "$genre", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    print("\n按体裁 (前10):")
    for doc in poems.aggregate(pipeline):
        genre = doc["_id"] or "未标注"
        print(f"  {genre}: {doc['count']} 首")

    # 作者数量
    pipeline = [
        {"$group": {"_id": "$author.name"}},
        {"$count": "total"},
    ]
    result = list(poems.aggregate(pipeline))
    if result:
        print(f"\n独立作者数: {result[0]['total']}")

    # 高产作者 TOP10
    pipeline = [
        {"$group": {"_id": "$author.name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    print("\n高产作者 TOP10:")
    for doc in poems.aggregate(pipeline):
        print(f"  {doc['_id']}: {doc['count']} 首")


if __name__ == "__main__":
    args = sys.argv[1:]

    if not args or args[0] == "stats":
        show_stats()
    elif args[0] in ("tang", "ci") and len(args) > 1:
        import_files(args[0], args[1:])
    elif args[0] == "auto" and len(args) > 1:
        auto_import(args[1])
    else:
        print(__doc__)
