# main.py
import uuid
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from pydantic import BaseModel

from app.game import (
    create_session, select_player_box, open_box,
    boxes_to_open_this_round, BOX_VALUES
)
from app.offer import calculate_offer, is_counter_offer_acceptable
from app.titles import (
    calculate_intuition_index, calculate_potential_value,
    assign_title, get_title_info
)

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# 内存会话存储
SESSIONS: dict[str, dict] = {}


# ── 请求体模型 ────────────────────────────────────────────────

class SelectBoxRequest(BaseModel):
    box_id: int


class OpenBoxRequest(BaseModel):
    box_id: int


class CounterOfferRequest(BaseModel):
    amount: int


# ── 内部辅助函数 ──────────────────────────────────────────────

def _get_session(session_id: str) -> dict:
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="会话不存在")
    return SESSIONS[session_id]


def _remaining_values(session: dict) -> list[int]:
    """获取所有未开箱子的价值列表（包含玩家箱子）。"""
    return [b["value"] for b in session["boxes"] if not b["opened"]]


def _finalize_game(session: dict, accepted_offer: bool) -> None:
    """游戏结束时计算评分和称号。"""
    session["game_over"] = True
    session["accepted_offer"] = accepted_offer
    player_box = session["boxes"][session["player_box_id"] - 1]
    session["intuition_index"] = calculate_intuition_index(player_box["value"], BOX_VALUES)
    session["potential_value"] = calculate_potential_value(player_box["value"])
    session["final_title"] = assign_title(
        intuition_index=session["intuition_index"],
        accepted_offer=accepted_offer,
        counter_offered=session["counter_offer_used"],
        counter_accepted=session.get("counter_accepted", False),
        rounds_played=session["current_round"],
    )


def _public_session(session: dict, session_id: str) -> dict:
    """向前端返回会话状态，未开箱子的价值在游戏结束前隐藏。"""
    boxes = []
    for b in session["boxes"]:
        box = {"id": b["id"], "opened": b["opened"]}
        if b["opened"] or session.get("game_over"):
            box["value"] = b["value"]
        boxes.append(box)
    return {
        "session_id": session_id,
        "boxes": boxes,
        "player_box_id": session["player_box_id"],
        "current_round": session["current_round"],
        "boxes_opened_this_round": session["boxes_opened_this_round"],
        "boxes_to_open_this_round": boxes_to_open_this_round(session["current_round"]),
        "offer_pending": session["offer_pending"],
        "counter_offer_used": session["counter_offer_used"],
        "game_over": session["game_over"],
        "last_offer": session["last_offer"],
        "accepted_offer": session.get("accepted_offer"),
        "final_title": session.get("final_title"),
        "intuition_index": session.get("intuition_index"),
        "potential_value": session.get("potential_value"),
    }


# ── 页面路由 ──────────────────────────────────────────────────

@app.get("/")
async def 首页(request: Request):
    return templates.TemplateResponse(request, "index.html")


# ── API 路由 ──────────────────────────────────────────────────

@app.post("/api/game/new")
async def 新游戏():
    session_id = str(uuid.uuid4())
    SESSIONS[session_id] = create_session()
    return _public_session(SESSIONS[session_id], session_id)


@app.get("/api/game/{session_id}/state")
async def 获取状态(session_id: str):
    return _public_session(_get_session(session_id), session_id)


@app.post("/api/game/{session_id}/select")
async def 选择箱子(session_id: str, body: SelectBoxRequest):
    session = _get_session(session_id)
    if session["player_box_id"] is not None:
        raise HTTPException(status_code=400, detail="已经选择过箱子了")
    try:
        select_player_box(session, body.box_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return _public_session(session, session_id)


@app.post("/api/game/{session_id}/open")
async def 开箱(session_id: str, body: OpenBoxRequest):
    session = _get_session(session_id)
    if session["player_box_id"] is None:
        raise HTTPException(status_code=400, detail="请先选择你的箱子")
    if session["offer_pending"]:
        raise HTTPException(status_code=400, detail="请先处理当前报价")
    if session["game_over"]:
        raise HTTPException(status_code=400, detail="游戏已结束")
    try:
        opened_box = open_box(session, body.box_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # 只剩玩家箱子 → 直接结算，不报价
    remaining_non_player = [
        b for b in session["boxes"]
        if not b["opened"] and b["id"] != session["player_box_id"]
    ]
    if len(remaining_non_player) == 0:
        _finalize_game(session, accepted_offer=False)
    elif session["offer_pending"]:
        remaining = _remaining_values(session)
        session["last_offer"] = calculate_offer(remaining)

    return {**_public_session(session, session_id), "opened_box": opened_box}


@app.post("/api/game/{session_id}/accept")
async def 接受报价(session_id: str):
    session = _get_session(session_id)
    if not session["offer_pending"]:
        raise HTTPException(status_code=400, detail="当前没有待处理的报价")
    session["offer_pending"] = False
    _finalize_game(session, accepted_offer=True)
    return {
        **_public_session(session, session_id),
        "title_info": get_title_info(session["final_title"]),
    }


@app.post("/api/game/{session_id}/reject")
async def 拒绝报价(session_id: str):
    session = _get_session(session_id)
    if not session["offer_pending"]:
        raise HTTPException(status_code=400, detail="当前没有待处理的报价")
    session["offer_pending"] = False
    session["current_round"] += 1
    session["boxes_opened_this_round"] = 0
    # 如果只剩玩家箱子，游戏结束
    remaining = [b for b in session["boxes"] if not b["opened"]]
    if len(remaining) == 1:
        _finalize_game(session, accepted_offer=False)
    return _public_session(session, session_id)


@app.post("/api/game/{session_id}/counter")
async def 还价(session_id: str, body: CounterOfferRequest):
    session = _get_session(session_id)
    if not session["offer_pending"]:
        raise HTTPException(status_code=400, detail="当前没有待处理的报价")
    if session["counter_offer_used"]:
        raise HTTPException(status_code=400, detail="本局还价机会已用完")
    session["counter_offer_used"] = True
    remaining = _remaining_values(session)
    accepted = is_counter_offer_acceptable(
        offer=session["last_offer"],
        counter=body.amount,
        remaining_count=len(remaining),
    )
    result: dict = {"counter_accepted": accepted}
    if accepted:
        session["counter_accepted"] = True
        session["offer_pending"] = False
        session["last_offer"] = body.amount
        _finalize_game(session, accepted_offer=True)
        result["title_info"] = get_title_info(session["final_title"])
    # 还价被拒绝时 offer_pending 保持 True，玩家仍可接受或拒绝原报价
    return {**_public_session(session, session_id), **result}
