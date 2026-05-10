# app/titles.py

TITLES = {
    "直觉大师": {
        "name": "直觉大师",
        "description": "你的直觉如神，精准把握市场脉搏，每一步都踩在节拍上！",
        "icon": "🔮",
    },
    "策略专家": {
        "name": "策略专家",
        "description": "稳中带锋，你的决策风格让对手摸不透底牌。",
        "icon": "🎯",
    },
    "谈判高手": {
        "name": "谈判高手",
        "description": "胆识过人！敢于还价，把主动权牢牢握在手中。",
        "icon": "🤝",
    },
    "市场大师": {
        "name": "市场大师",
        "description": "深谙市场，洞察先机，是罕见的潜力型交易员！",
        "icon": "📈",
    },
    "幸运交易师": {
        "name": "幸运交易师",
        "description": "运气也是实力的一部分，保持这份直觉继续前行！",
        "icon": "🍀",
    },
}


def calculate_intuition_index(player_value: int, all_values: list[int]) -> int:
    """计算直觉指数：玩家箱子价值在所有价值中的百分位（0-100）。"""
    sorted_vals = sorted(all_values)
    rank = sorted_vals.index(player_value) + 1
    return round((rank / len(all_values)) * 100)


def calculate_potential_value(player_box_value: int) -> int:
    """潜力值即玩家箱子的实际价值。"""
    return player_box_value


def assign_title(
    intuition_index: int,
    accepted_offer: bool,
    counter_offered: bool,
    rounds_played: int,
) -> str:
    """根据游戏表现分配称号，优先级从高到低。"""
    if intuition_index >= 80:
        return "直觉大师"
    if accepted_offer and rounds_played <= 3:
        return "策略专家"
    if counter_offered:
        return "谈判高手"
    if rounds_played >= 6:
        return "市场大师"
    return "幸运交易师"


def get_title_info(title_name: str) -> dict:
    return TITLES.get(title_name, TITLES["幸运交易师"])
