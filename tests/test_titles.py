# tests/test_titles.py
import pytest
from app.titles import calculate_intuition_index, calculate_potential_value, assign_title
from app.game import BOX_VALUES


def test_直觉指数_顶级箱子():
    # 价值 1000（最高）→ 排名 26/26 → 指数 100
    idx = calculate_intuition_index(player_value=1000, all_values=BOX_VALUES)
    assert idx == 100


def test_直觉指数_最低箱子():
    # 价值 1（最低），排名第 1，共 26 个 → round(1/26*100) = 4
    idx = calculate_intuition_index(player_value=1, all_values=BOX_VALUES)
    assert idx == 4


def test_直觉指数_中间箱子():
    idx = calculate_intuition_index(player_value=500, all_values=BOX_VALUES)
    assert 50 <= idx <= 90


def test_潜力值等于玩家箱子价值():
    assert calculate_potential_value(player_box_value=750) == 750


def test_称号_直觉大师():
    title = assign_title(
        intuition_index=85, accepted_offer=False,
        counter_offered=False, rounds_played=8
    )
    assert title == "直觉大师"


def test_称号_策略专家():
    title = assign_title(
        intuition_index=50, accepted_offer=True,
        counter_offered=False, rounds_played=2
    )
    assert title == "策略专家"


def test_称号_谈判高手():
    title = assign_title(
        intuition_index=60, accepted_offer=True,
        counter_offered=True, rounds_played=4
    )
    assert title == "谈判高手"


def test_称号_市场大师():
    title = assign_title(
        intuition_index=60, accepted_offer=False,
        counter_offered=False, rounds_played=7
    )
    assert title == "市场大师"


def test_称号_幸运交易师_兜底():
    title = assign_title(
        intuition_index=40, accepted_offer=False,
        counter_offered=False, rounds_played=3
    )
    assert title == "幸运交易师"
