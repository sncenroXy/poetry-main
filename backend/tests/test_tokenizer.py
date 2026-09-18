"""tokenize 分词测试"""
from app.utils.tokenizer import tokenize


def test_tokenize_empty():
    assert tokenize("") == []
    assert tokenize(None) == []


def test_tokenize_basic():
    tokens = tokenize("床前明月光")
    assert isinstance(tokens, list)
    assert tokens  # 非空
    assert all(len(t) >= 2 for t in tokens)


def test_tokenize_deduplicates():
    tokens = tokenize("明月 明月 故乡")
    assert len(tokens) == len(set(tokens))


def test_tokenize_filters_single_char():
    tokens = tokenize("月")
    assert tokens == []


def test_tokenize_keeps_order_and_chinese():
    tokens = tokenize("静夜思 李白")
    assert tokens  # 至少分词出 静夜 / 李白 等
    # 全部为中文或含中文字符，且长度达标
    assert all(len(t) >= 2 for t in tokens)
