# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_新游戏返回会话ID():
    resp = client.post("/api/game/new")
    assert resp.status_code == 200
    data = resp.json()
    assert "session_id" in data
    assert len(data["boxes"]) == 26
    assert data["player_box_id"] is None


def test_选择箱子():
    resp = client.post("/api/game/new")
    sid = resp.json()["session_id"]
    resp2 = client.post(f"/api/game/{sid}/select", json={"box_id": 13})
    assert resp2.status_code == 200
    assert resp2.json()["player_box_id"] == 13


def test_选择无效箱子返回400():
    resp = client.post("/api/game/new")
    sid = resp.json()["session_id"]
    resp2 = client.post(f"/api/game/{sid}/select", json={"box_id": 99})
    assert resp2.status_code == 400


def test_开箱():
    resp = client.post("/api/game/new")
    sid = resp.json()["session_id"]
    client.post(f"/api/game/{sid}/select", json={"box_id": 1})
    resp2 = client.post(f"/api/game/{sid}/open", json={"box_id": 2})
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["opened_box"]["id"] == 2
    assert data["opened_box"]["opened"] is True


def test_第1轮结束后出现报价():
    resp = client.post("/api/game/new")
    sid = resp.json()["session_id"]
    client.post(f"/api/game/{sid}/select", json={"box_id": 1})
    for box_id in range(2, 8):  # 开 6 个箱子
        client.post(f"/api/game/{sid}/open", json={"box_id": box_id})
    state = client.get(f"/api/game/{sid}/state").json()
    assert state["offer_pending"] is True
    assert state["last_offer"] is not None


def test_接受报价结束游戏():
    resp = client.post("/api/game/new")
    sid = resp.json()["session_id"]
    client.post(f"/api/game/{sid}/select", json={"box_id": 1})
    for box_id in range(2, 8):
        client.post(f"/api/game/{sid}/open", json={"box_id": box_id})
    resp2 = client.post(f"/api/game/{sid}/accept")
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["game_over"] is True
    assert data["final_title"] is not None
    assert data["intuition_index"] is not None


def test_拒绝报价推进到下一轮():
    resp = client.post("/api/game/new")
    sid = resp.json()["session_id"]
    client.post(f"/api/game/{sid}/select", json={"box_id": 1})
    for box_id in range(2, 8):
        client.post(f"/api/game/{sid}/open", json={"box_id": box_id})
    resp2 = client.post(f"/api/game/{sid}/reject")
    assert resp2.status_code == 200
    data = resp2.json()
    assert data["offer_pending"] is False
    assert data["current_round"] == 1


def test_还价在区间内被接受():
    resp = client.post("/api/game/new")
    sid = resp.json()["session_id"]
    client.post(f"/api/game/{sid}/select", json={"box_id": 1})
    for box_id in range(2, 8):
        client.post(f"/api/game/{sid}/open", json={"box_id": box_id})
    state = client.get(f"/api/game/{sid}/state").json()
    offer = state["last_offer"]
    counter = round(offer * 1.05)  # 高于报价 5%，在前期接受区间内
    resp2 = client.post(f"/api/game/{sid}/counter", json={"amount": counter})
    assert resp2.status_code == 200
    assert resp2.json()["counter_accepted"] is True
    assert resp2.json()["game_over"] is True


def test_还价过高被拒绝():
    resp = client.post("/api/game/new")
    sid = resp.json()["session_id"]
    client.post(f"/api/game/{sid}/select", json={"box_id": 1})
    for box_id in range(2, 8):
        client.post(f"/api/game/{sid}/open", json={"box_id": box_id})
    state = client.get(f"/api/game/{sid}/state").json()
    offer = state["last_offer"]
    counter = round(offer * 3.0)  # 高于报价 200%，超出接受区间
    resp2 = client.post(f"/api/game/{sid}/counter", json={"amount": counter})
    assert resp2.status_code == 200
    assert resp2.json()["counter_accepted"] is False
    assert resp2.json()["game_over"] is False  # 原报价仍待处理


def test_最后一箱打开时直接结算无报价():
    resp = client.post("/api/game/new")
    sid = resp.json()["session_id"]
    client.post(f"/api/game/{sid}/select", json={"box_id": 1})
    # 拒绝所有报价，开完全部非玩家箱子
    for box_id in range(2, 27):
        state = client.get(f"/api/game/{sid}/state").json()
        if state["game_over"]:
            break
        if state["offer_pending"]:
            client.post(f"/api/game/{sid}/reject")
        client.post(f"/api/game/{sid}/open", json={"box_id": box_id})
    final = client.get(f"/api/game/{sid}/state").json()
    assert final["game_over"] is True
    assert final["offer_pending"] is False


def test_第二次还价返回400():
    resp = client.post("/api/game/new")
    sid = resp.json()["session_id"]
    client.post(f"/api/game/{sid}/select", json={"box_id": 1})
    for box_id in range(2, 8):
        client.post(f"/api/game/{sid}/open", json={"box_id": box_id})
    state = client.get(f"/api/game/{sid}/state").json()
    offer = state["last_offer"]
    # 第一次还价（过高，被拒绝）
    client.post(f"/api/game/{sid}/counter", json={"amount": round(offer * 3.0)})
    # 第二次还价 → 应返回 400
    resp2 = client.post(f"/api/game/{sid}/counter", json={"amount": 100})
    assert resp2.status_code == 400
