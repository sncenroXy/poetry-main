"""中文分词工具 — 基于 jieba，用于诗词检索的倒排索引

jieba 首次加载词典较慢（约 1s），因此惰性初始化；之后缓存复用。
"""
from typing import List

import jieba

_initialized = False


def _ensure_init() -> None:
    global _initialized
    if not _initialized:
        jieba.initialize()
        _initialized = True


def tokenize(text: str, min_len: int = 2) -> List[str]:
    """对文本做 jieba 分词，返回去重、保序的关键词列表。

    - 过滤长度 < min_len 的 token（避免为每个单字建索引，索引爆炸）
    - 过滤纯空白/标点 token
    - 去重但保持首次出现顺序
    """
    if not text:
        return []
    _ensure_init()

    tokens: List[str] = []
    seen = set()
    for word in jieba.cut(text):
        w = word.strip()
        if len(w) < min_len:
            continue
        if w in seen:
            continue
        # 过滤纯标点/空白片段
        if not any(ch.isalnum() or "一" <= ch <= "鿿" for ch in w):
            continue
        seen.add(w)
        tokens.append(w)
    return tokens
