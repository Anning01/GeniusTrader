# tests/test_titles.py
import pytest
from app.titles import calculate_intuition_index, calculate_potential_value, assign_title
from app.game import BOX_VALUES


def test_直觉指数_顶级箱子():
    idx = calculate_intuition_index(player_value=1_000_000, all_values=BOX_VALUES)
    assert idx == 100


def test_直觉指数_最低箱子():
    idx = calculate_intuition_index(player_value=1, all_values=BOX_VALUES)
    assert idx == 4


def test_直觉指数_中间箱子():
    # 500 在新价值表中排名第 12，round(12/26*100)=46
    idx = calculate_intuition_index(player_value=500, all_values=BOX_VALUES)
    assert 40 <= idx <= 55


def test_潜力值等于玩家箱子价值():
    assert calculate_potential_value(player_box_value=750) == 750


# ── 12 个称号覆盖测试 ─────────────────────────────────────────

def _t(intuition, accepted, counter_offered=False, counter_accepted=False, rounds=0):
    return assign_title(
        intuition_index=intuition,
        accepted_offer=accepted,
        counter_offered=counter_offered,
        counter_accepted=counter_accepted,
        rounds_played=rounds,
    )


def test_隐藏成就_百万传奇():
    # 直觉满分（$1M 箱子）且坚持到底
    assert _t(100, False, rounds=8) == "百万传奇"


def test_隐藏成就_最贵的遗憾():
    # 直觉满分（$1M 箱子）但接受了报价
    assert _t(100, True, rounds=1) == "最贵的遗憾"


def test_称号_天启交易师():
    assert _t(90, False, rounds=8) == "天启交易师"


def test_称号_谈判艺术家():
    assert _t(60, True, counter_offered=True, counter_accepted=True, rounds=1) == "谈判艺术家"


def test_称号_意志砥柱():
    assert _t(80, False, rounds=8) == "意志砥柱"


def test_称号_精准猎手():
    assert _t(75, True, rounds=2) == "精准猎手"


def test_称号_直觉信徒():
    # rounds=4 避免与精准猎手（rounds 1-3）重叠
    assert _t(85, True, rounds=4) == "直觉信徒"


def test_称号_闪电决断者():
    assert _t(50, True, rounds=0) == "闪电决断者"


def test_称号_卧龙待醒():
    assert _t(60, True, rounds=5) == "卧龙待醒"


def test_称号_戏剧制造者():
    assert _t(60, True, counter_offered=True, counter_accepted=False, rounds=2) == "戏剧制造者"


def test_称号_赌徒哲学家():
    assert _t(20, False, rounds=8) == "赌徒哲学家"


def test_称号_孤胆英雄():
    assert _t(50, False, rounds=8) == "孤胆英雄"


def test_称号_淡然成交者():
    assert _t(40, True, rounds=1) == "淡然成交者"


def test_称号_随遇而安者_兜底():
    # 直觉40，接受，第3轮（不满足任何前面规则）
    assert _t(40, True, rounds=3) == "随遇而安者"
