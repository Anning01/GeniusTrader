# app/offer.py
import random

# 各阶段报价浮动区间（相对于剩余箱子均值）
FLOAT_RANGES = {
    "early": (-0.10, 0.10),   # 前期：-10% ~ +10%
    "mid":   (-0.05, 0.20),   # 中期：-5%  ~ +20%
    "late":  (0.00,  0.25),   # 后期：0%   ~ +25%
    "final": (0.10,  0.35),   # 最后：+10% ~ +35%
}

# 各阶段还价接受上限（还价必须严格高于报价，且不超过此倍数）
COUNTER_RANGES = {
    "early": 1.30,
    "mid":   1.35,
    "late":  1.38,
    "final": 1.40,
}


def get_phase(remaining_count: int) -> str:
    """根据剩余箱子数量判断当前游戏阶段。"""
    if remaining_count >= 15:
        return "early"
    elif remaining_count >= 8:
        return "mid"
    elif remaining_count >= 4:
        return "late"
    return "final"


def calculate_offer(remaining_values: list[int]) -> int:
    """计算 AI 报价 = 剩余均值 × (1 + 随机浮动)。"""
    mean_value = sum(remaining_values) / len(remaining_values)
    phase = get_phase(len(remaining_values))
    lo, hi = FLOAT_RANGES[phase]
    multiplier = 1 + random.uniform(lo, hi)
    return round(mean_value * multiplier)


def is_counter_offer_acceptable(offer: int, counter: int, remaining_count: int) -> bool:
    """还价必须严格高于报价，且不超过当前阶段上限倍数。"""
    if counter <= offer:
        return False
    hi_ratio = COUNTER_RANGES[get_phase(remaining_count)]
    return counter <= round(offer * hi_ratio)
