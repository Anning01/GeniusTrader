# tests/test_offer.py
import pytest
from app.offer import get_phase, calculate_offer, is_counter_offer_acceptable


def test_箱子多时为前期阶段():
    assert get_phase(26) == "early"
    assert get_phase(15) == "early"


def test_中期阶段():
    assert get_phase(14) == "mid"
    assert get_phase(8) == "mid"


def test_后期阶段():
    assert get_phase(7) == "late"
    assert get_phase(4) == "late"


def test_最后阶段():
    assert get_phase(3) == "final"
    assert get_phase(1) == "final"


def test_前期报价在合理区间内():
    # 15 个相同元素 → 均值 500，前期浮动 -10%~+10% → 450~550
    remaining = [500] * 15
    for _ in range(100):
        offer = calculate_offer(remaining)
        assert 450 <= offer <= 550, f"报价 {offer} 超出前期区间"


def test_最后阶段报价高于均值():
    # 剩余 [1, 1000] → 均值约 500.5，最后阶段浮动 +10%~+35%
    remaining = [1, 1000]
    for _ in range(50):
        offer = calculate_offer(remaining)
        assert offer >= 500, f"最后阶段报价 {offer} 不应低于均值"


def test_还价在接受区间内():
    # 前期阶段接受区间：报价 × [0.85, 1.30]
    assert is_counter_offer_acceptable(offer=500, counter=450, remaining_count=20) is True
    assert is_counter_offer_acceptable(offer=500, counter=600, remaining_count=20) is True


def test_还价过低被拒绝():
    assert is_counter_offer_acceptable(offer=500, counter=100, remaining_count=20) is False


def test_还价过高被拒绝():
    assert is_counter_offer_acceptable(offer=500, counter=900, remaining_count=20) is False
