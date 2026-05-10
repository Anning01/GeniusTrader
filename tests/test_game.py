# tests/test_game.py
import pytest
from app.game import create_session, BOX_VALUES, select_player_box, open_box, boxes_to_open_this_round


def test_创建会话有26个箱子():
    session = create_session()
    assert len(session["boxes"]) == 26


def test_所有箱子价值已分配():
    session = create_session()
    values = [b["value"] for b in session["boxes"]]
    assert sorted(values) == sorted(BOX_VALUES)


def test_箱子顺序已打乱():
    session1 = create_session()
    session2 = create_session()
    vals1 = [b["value"] for b in session1["boxes"]]
    vals2 = [b["value"] for b in session2["boxes"]]
    # 26! 分之一的概率完全相同，可安全断言
    assert vals1 != vals2


def test_所有箱子初始为关闭状态():
    session = create_session()
    assert all(not b["opened"] for b in session["boxes"])


def test_会话初始状态():
    session = create_session()
    assert session["player_box_id"] is None
    assert session["current_round"] == 0
    assert session["boxes_opened_this_round"] == 0
    assert session["offer_pending"] is False
    assert session["counter_offer_used"] is False
    assert session["game_over"] is False
    assert session["last_offer"] is None


# ── 轮次逻辑测试 ──────────────────────────────────────────────

def test_选择玩家箱子():
    session = create_session()
    select_player_box(session, 13)
    assert session["player_box_id"] == 13


def test_选择无效箱子抛出异常():
    session = create_session()
    with pytest.raises(ValueError, match="箱子编号无效"):
        select_player_box(session, 27)


def test_第1轮需要开6个箱子():
    assert boxes_to_open_this_round(0) == 6


def test_第2轮需要开5个箱子():
    assert boxes_to_open_this_round(1) == 5


def test_第6轮及之后每轮1个():
    assert boxes_to_open_this_round(5) == 1
    assert boxes_to_open_this_round(10) == 1


def test_开箱后箱子标记为已开():
    session = create_session()
    select_player_box(session, 1)
    opened_box = open_box(session, 2)
    assert opened_box["opened"] is True
    assert session["boxes"][1]["opened"] is True  # id=2 对应索引 1


def test_不能开玩家自己的箱子():
    session = create_session()
    select_player_box(session, 1)
    with pytest.raises(ValueError, match="不能开玩家"):
        open_box(session, 1)


def test_不能重复开同一个箱子():
    session = create_session()
    select_player_box(session, 1)
    open_box(session, 2)
    with pytest.raises(ValueError, match="已经被打开"):
        open_box(session, 2)


def test_本轮开完后触发报价():
    session = create_session()
    select_player_box(session, 1)
    for box_id in range(2, 8):  # 开 2-7 号箱，共 6 个
        open_box(session, box_id)
    assert session["offer_pending"] is True


def test_仅剩玩家箱子时不触发报价():
    session = create_session()
    select_player_box(session, 1)
    # 开完所有非玩家箱子（手动清空轮次限制）
    for box_id in range(2, 27):
        if session["offer_pending"]:
            session["offer_pending"] = False
            session["current_round"] += 1
            session["boxes_opened_this_round"] = 0
        open_box(session, box_id)
    assert session["offer_pending"] is False


def test_报价结束后轮次递增():
    session = create_session()
    select_player_box(session, 1)
    for box_id in range(2, 8):
        open_box(session, box_id)
    # 模拟报价处理完成
    session["offer_pending"] = False
    session["current_round"] += 1
    session["boxes_opened_this_round"] = 0
    assert session["current_round"] == 1
