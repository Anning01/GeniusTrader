# app/game.py
import random

BOX_VALUES = [
    1, 2, 5, 10, 25, 50, 75, 100, 200, 300,
    400, 500, 750, 1_000, 5_000, 10_000, 25_000, 50_000,
    75_000, 100_000, 200_000, 300_000, 400_000, 500_000, 750_000, 1_000_000
]

# 每轮开箱数量：6、5、4、3、2、之后每轮 1 个
ROUNDS_SCHEDULE = [6, 5, 4, 3, 2, 1, 1, 1, 1, 1,
                   1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]


def create_session() -> dict:
    shuffled = random.sample(BOX_VALUES, len(BOX_VALUES))
    boxes = [{"id": i + 1, "value": shuffled[i], "opened": False} for i in range(26)]
    return {
        "boxes": boxes,
        "player_box_id": None,
        "current_round": 0,
        "boxes_opened_this_round": 0,
        "offer_pending": False,
        "counter_offer_used": False,
        "counter_accepted": False,
        "game_over": False,
        "last_offer": None,
        "accepted_offer": False,
        "final_title": None,
        "intuition_index": None,
        "potential_value": None,
    }


def select_player_box(session: dict, box_id: int) -> None:
    if box_id < 1 or box_id > 26:
        raise ValueError(f"箱子编号无效：{box_id}")
    session["player_box_id"] = box_id


def boxes_to_open_this_round(round_index: int) -> int:
    if round_index < len(ROUNDS_SCHEDULE):
        return ROUNDS_SCHEDULE[round_index]
    return 1


def open_box(session: dict, box_id: int) -> dict:
    if box_id == session["player_box_id"]:
        raise ValueError("不能开玩家自己的箱子")
    box = session["boxes"][box_id - 1]
    if box["opened"]:
        raise ValueError(f"{box_id} 号箱子已经被打开")
    box["opened"] = True
    session["boxes_opened_this_round"] += 1

    # 如果只剩玩家箱子，游戏直接结束，不触发报价
    remaining_non_player = sum(
        1 for b in session["boxes"]
        if not b["opened"] and b["id"] != session["player_box_id"]
    )
    if remaining_non_player > 0:
        if session["boxes_opened_this_round"] >= boxes_to_open_this_round(session["current_round"]):
            session["offer_pending"] = True
    return box
