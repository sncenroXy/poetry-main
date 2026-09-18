"""检索服务"""
import re
from typing import List, Optional, Tuple, Dict, Any
from app.database import poems_collection
from app.models import Poem
from app.utils.tokenizer import tokenize


async def get_filter_options() -> Dict[str, List[str]]:
    """获取所有可用的筛选项（朝代、体裁、作者、标签）"""
    dynasties = await poems_collection.distinct("dynasty")
    genres = await poems_collection.distinct("genre")
    authors = await poems_collection.distinct("author.name")
    tags = await poems_collection.distinct("tags")

    # 过滤 None/空值并排序
    return {
        "dynasties": sorted([d for d in dynasties if d]),
        "genres": sorted([g for g in genres if g]),
        "authors": sorted([a for a in authors if a]),
        "tags": sorted([t for t in tags if t]),
    }


def _build_filter(
    dynasty: Optional[str] = None,
    genre: Optional[str] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
) -> Dict[str, Any]:
    """构建 MongoDB 查询过滤条件"""
    query: Dict[str, Any] = {}
    if dynasty:
        query["dynasty"] = dynasty
    if genre:
        query["genre"] = genre
    if author:
        query["author.name"] = author
    if tag:
        query["tags"] = tag
    return query


async def find_poems_filtered(
    page: int = 1,
    page_size: int = 18,
    dynasty: Optional[str] = None,
    genre: Optional[str] = None,
    author: Optional[str] = None,
    tag: Optional[str] = None,
) -> Tuple[List[Poem], int]:
    """按分类筛选诗词（分页）"""
    query = _build_filter(dynasty, genre, author, tag)
    if not query:
        return await find_all_poems(page, page_size)

    total = await poems_collection.count_documents(query)
    skip = (page - 1) * page_size
    cursor = poems_collection.find(query).sort("sort_order", 1).skip(skip).limit(page_size)
    poems = []
    async for doc in cursor:
        doc["id"] = doc.pop("_id", doc.get("id"))
        poems.append(Poem(**doc))
    return poems, total


def _regex_query(term: str) -> Dict[str, Any]:
    """子串模糊匹配查询（无索引，作为关键词索引的兜底）"""
    return {
        "$or": [
            {"title": {"$regex": term}},
            {"author.name": {"$regex": term}},
            {"content": {"$regex": term}},
            {"tags": {"$regex": term}},
        ]
    }


def build_search_query(q: str) -> Optional[Dict[str, Any]]:
    """构建搜索查询：优先走 keywords 倒排索引（jieba 分词）。

    返回 None 表示无法用索引（如单字查询），应回退 $regex。
    """
    tokens = tokenize(q.strip())
    if not tokens:
        return None
    # 所有关键词都必须命中（$all 保证召回精度）
    return {"keywords": {"$all": tokens}}


async def search_poems(q: Optional[str] = None, page: int = 1, page_size: int = 18) -> Tuple[List[Poem], int]:
    """通用检索：按诗句/诗名/作者/关键词模糊检索，带分页"""
    if not q or not q.strip():
        return await find_all_poems(page, page_size)

    term = q.strip()
    escaped = re.escape(term)

    # 优先走关键词索引；单字查询或无有效分词时回退 regex
    query_filter = build_search_query(term)
    if query_filter is None:
        query_filter = _regex_query(escaped)
        total = await poems_collection.count_documents(query_filter)
    else:
        total = await poems_collection.count_documents(query_filter)
        if total == 0:
            # 索引无命中（可能是关键词尚未回填或分词不匹配），兜底走 regex 保证召回
            query_filter = _regex_query(escaped)
            total = await poems_collection.count_documents(query_filter)

    skip = (page - 1) * page_size
    cursor = poems_collection.find(query_filter).skip(skip).limit(page_size)
    poems = []
    async for doc in cursor:
        doc["id"] = doc.pop("_id", doc.get("id"))
        poems.append(Poem(**doc))
    return poems, total


async def find_all_poems(page: int = 1, page_size: int = 18) -> Tuple[List[Poem], int]:
    """获取所有诗词（分页，按 sort_order 随机顺序）"""
    total = await poems_collection.count_documents({})
    skip = (page - 1) * page_size
    cursor = poems_collection.find().sort("sort_order", 1).skip(skip).limit(page_size)
    poems = []
    async for doc in cursor:
        doc["id"] = doc.pop("_id", doc.get("id"))
        poems.append(Poem(**doc))
    return poems, total


async def find_poem_by_id(poem_id: str) -> Optional[Poem]:
    """根据 ID 查找诗词"""
    doc = await poems_collection.find_one({"_id": poem_id})
    if not doc:
        return None
    doc["id"] = doc.pop("_id")
    return Poem(**doc)


async def find_poems_by_author(name: str, page: int = 1, page_size: int = 18) -> Tuple[List[Poem], int]:
    """根据作者名检索（分页）"""
    if not name or not name.strip():
        return await find_all_poems(page, page_size)

    term = re.escape(name.strip())
    # 前缀锚定，可用 author.name 索引（原无锚定子串会退化为全表扫描）
    query_filter = {"author.name": {"$regex": f"^{term}"}}
    total = await poems_collection.count_documents(query_filter)
    skip = (page - 1) * page_size
    cursor = poems_collection.find(query_filter).skip(skip).limit(page_size)
    poems = []
    async for doc in cursor:
        doc["id"] = doc.pop("_id", doc.get("id"))
        poems.append(Poem(**doc))
    return poems, total
