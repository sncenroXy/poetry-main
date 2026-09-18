"""飞花令接龙匹配逻辑测试（纯函数，无需数据库）"""
from app.services.challenge_service import match_next_lines, is_valid_next

JINGYE = ["床前明月光", "疑是地上霜", "举头望明月", "低头思故乡"]


def test_match_next_lines_single():
    assert match_next_lines(JINGYE, "床前明月光") == ["疑是地上霜"]
    assert match_next_lines(JINGYE, "举头望明月") == ["低头思故乡"]


def test_match_next_lines_last_line_has_no_next():
    assert match_next_lines(JINGYE, "低头思故乡") == []


def test_match_next_lines_not_found():
    assert match_next_lines(JINGYE, "不存在的句子") == []


def test_match_next_lines_empty_inputs():
    assert match_next_lines([], "床前明月光") == []
    assert match_next_lines(JINGYE, "") == []


def test_is_valid_next_true():
    assert is_valid_next(JINGYE, "床前明月光", "疑是地上霜") is True


def test_is_valid_next_false_non_adjacent():
    # 「低头思故乡」不是「床前明月光」的紧接下句
    assert is_valid_next(JINGYE, "床前明月光", "低头思故乡") is False


def test_is_valid_next_empty():
    assert is_valid_next(JINGYE, "", "疑是地上霜") is False
    assert is_valid_next(JINGYE, "床前明月光", "") is False
    assert is_valid_next([], "床前明月光", "疑是地上霜") is False
