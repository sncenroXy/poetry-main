"""搜索查询构造测试"""
from app.services.search_service import build_search_query, _build_filter, _regex_query


def test_build_search_query_multi_char():
    q = build_search_query("明月")
    assert q is not None
    assert "keywords" in q
    assert "$all" in q["keywords"]
    assert q["keywords"]["$all"]  # 非空分词列表


def test_build_search_query_single_char_returns_none():
    # 单字查询无法用索引（min_len=2），回退 regex
    assert build_search_query("月") is None


def test_build_search_query_empty():
    assert build_search_query("") is None
    assert build_search_query("   ") is None


def test_regex_query_covers_fields():
    q = _regex_query("静夜")
    fields = {list(cond.keys())[0] for cond in q["$or"]}
    assert fields == {"title", "author.name", "content", "tags"}


def test_build_filter():
    assert _build_filter() == {}
    assert _build_filter(dynasty="唐", author="李白") == {
        "dynasty": "唐",
        "author.name": "李白",
    }
    assert _build_filter(genre="五言绝句", tag="唐诗") == {
        "genre": "五言绝句",
        "tags": "唐诗",
    }
