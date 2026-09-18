"""parse_llm_json 多级容错解析测试"""
import pytest

from app.utils.llm import parse_llm_json


def test_parse_valid_json_object():
    raw = '{"title": "静夜思", "content": ["床前明月光", "疑是地上霜"]}'
    data = parse_llm_json(raw)
    assert data["title"] == "静夜思"
    assert data["content"] == ["床前明月光", "疑是地上霜"]


def test_parse_markdown_fence():
    raw = '```json\n{"title": "静夜思", "content": ["床前明月光"]}\n```'
    data = parse_llm_json(raw)
    assert data["title"] == "静夜思"


def test_parse_json_prefix_no_fence():
    raw = 'json\n{"title": "静夜思"}'
    data = parse_llm_json(raw)
    assert data["title"] == "静夜思"


def test_parse_prose_around_json():
    """前后有说明文字，应通过括号切片提取"""
    raw = '好的，以下是结果：\n{"title": "静夜思", "content": ["床前明月光"]}\n希望你喜欢。'
    data = parse_llm_json(raw)
    assert data["title"] == "静夜思"
    assert data["content"] == ["床前明月光"]


def test_parse_json5_trailing_comma_single_quote():
    """json5 容忍单引号和尾逗号"""
    raw = "{'title': '静夜思', 'content': ['床前明月光',],}"
    data = parse_llm_json(raw)
    assert data["title"] == "静夜思"
    assert data["content"] == ["床前明月光"]


def test_parse_broken_json_field_extraction():
    """缺少闭合括号，退到正则字段提取"""
    raw = '{"title": "静夜思"'
    data = parse_llm_json(raw)
    assert data["title"] == "静夜思"


def test_parse_garbage_raises():
    with pytest.raises(ValueError):
        parse_llm_json("这完全不是 JSON，也没有任何可识别的字段。")
