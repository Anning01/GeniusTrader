// static/js/game.js
'use strict';

let STATE = {
  sessionId: null,
  session: null,
};

// ── API 客户端 ────────────────────────────────────────────────
const API = {
  async post(path, body = null) {
    const opts = { method: 'POST', headers: { 'Content-Type': 'application/json' } };
    if (body) opts.body = JSON.stringify(body);
    const resp = await fetch(path, opts);
    if (!resp.ok) {
      const err = await resp.json().catch(() => ({ detail: '请求失败' }));
      throw new Error(err.detail || '请求失败');
    }
    return resp.json();
  },
  async get(path) {
    const resp = await fetch(path);
    return resp.json();
  },
};

// ── 界面辅助函数 ──────────────────────────────────────────────
function show(screenId) {
  document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
  document.getElementById(screenId).classList.add('active');
}
function showModal(id)  { document.getElementById(id).classList.remove('hidden'); }
function hideModal(id)  { document.getElementById(id).classList.add('hidden'); }
function toggleHidden(id, hidden) { document.getElementById(id).classList.toggle('hidden', hidden); }
function setAiMessage(msg) { document.getElementById('ai-message').textContent = msg; }

function updateStats(session) {
  document.getElementById('stat-potential').textContent  = session.potential_value != null ? fmt(session.potential_value) : '—';
  document.getElementById('stat-intuition').textContent  = session.intuition_index ?? '—';
}

function updateProgress(session) {
  const round     = session.current_round + 1;
  const opened    = session.boxes_opened_this_round;
  const needed    = session.boxes_to_open_this_round;
  const remaining = session.boxes.filter(b => !b.opened).length;
  document.getElementById('round-label').textContent        = `第 ${round} 轮`;
  document.getElementById('boxes-opened-label').textContent = `已开: ${opened} / ${needed}`;
  document.getElementById('remaining-label').textContent    = `剩余: ${remaining}`;
}

// ── 金额榜 ───────────────────────────────────────────────────
const ALL_VALUES   = [1,2,5,10,25,50,75,100,200,300,400,500,750,1000,5000,10000,25000,50000,75000,100000,200000,300000,400000,500000,750000,1000000];
const LEFT_VALUES  = ALL_VALUES.slice(0, 13);
const RIGHT_VALUES = ALL_VALUES.slice(13);

function fmt(v) {
  if (v == null) return '—';
  return '$' + Number(v).toLocaleString('en-US');
}

function fmtShort(v) {
  if (v >= 1_000_000) return '$1M';
  if (v >= 1_000)     return '$' + (v / 1000) + 'K';
  return '$' + v;
}

function renderValueBoard(session) {
  renderValueBoardInto(session, 'value-panel-left', 'value-panel-right');
}

// ── 箱子网格渲染 ──────────────────────────────────────────────
function renderBoxes(session) {
  const grid = document.getElementById('boxes-grid');
  grid.innerHTML = '';
  session.boxes.forEach(box => {
    const el = document.createElement('div');
    el.className = 'box-item';
    el.dataset.id = box.id;

    if (box.id === session.player_box_id) {
      el.classList.add('selected');
      el.innerHTML = `<span class="box-number">${box.id}</span><span class="box-my-label">我的箱子</span>`;
    } else if (box.opened) {
      el.classList.add('opened');
      const valStr = box.value !== undefined ? fmtShort(box.value) : '';
      el.innerHTML = `<span class="box-value">${valStr}</span>`;
    } else {
      el.innerHTML = `<span class="box-number">${box.id}</span>`;
      el.addEventListener('click', () => handleBoxClick(box.id));
    }
    grid.appendChild(el);
  });
}

// ── 游戏主流程 ────────────────────────────────────────────────
async function startNewGame() {
  try {
    const data = await API.post('/api/game/new');
    STATE.sessionId = data.session_id;
    STATE.session   = data;
    show('screen-game');
    renderBoxes(data);
    renderValueBoard(data);
    updateProgress(data);
    setAiMessage('从 26 个神秘箱子中，选择一个作为你的箱子！');
    document.getElementById('btn-continue').disabled         = true;
    document.getElementById('btn-my-box').textContent        = '我的箱子';
    document.getElementById('btn-my-box').disabled           = true;
  } catch (e) {
    alert('启动游戏失败：' + e.message);
  }
}

async function handleBoxClick(boxId) {
  const session = STATE.session;
  if (!session.player_box_id) {
    // 选择玩家自己的箱子
    try {
      const data = await API.post(`/api/game/${STATE.sessionId}/select`, { box_id: boxId });
      STATE.session = data;
      renderBoxes(data);
      renderValueBoard(data);
      setAiMessage(`你选择了 ${boxId} 号箱子！点击其他箱子开始探索，或点击「继续开箱」随机开启。`);
      document.getElementById('btn-continue').disabled  = false;
      document.getElementById('btn-my-box').textContent = `我的箱子 · ${boxId} 号`;
      document.getElementById('btn-my-box').disabled    = false;
    } catch (e) {
      setAiMessage('⚠️ ' + e.message);
    }
  } else if (!session.offer_pending && !session.game_over) {
    await openSingleBox(boxId);
  }
}

async function openSingleBox(boxId) {
  try {
    const data = await API.post(`/api/game/${STATE.sessionId}/open`, { box_id: boxId });
    STATE.session = data;

    // 开箱动画
    const el = document.querySelector(`.box-item[data-id="${boxId}"]`);
    if (el) el.classList.add('opening');
    setTimeout(() => { renderBoxes(data); renderValueBoard(data); }, 420);

    updateProgress(data);
    updateStats(data);

    if (data.game_over) {
      setTimeout(() => showSettlement(data), 600);
    } else if (data.offer_pending) {
      document.getElementById('btn-continue').disabled = true;
      setTimeout(() => showOffer(data), 950);
    }
  } catch (e) {
    setAiMessage('⚠️ ' + e.message);
  }
}

async function handleContinue() {
  // 随机选一个未开且非玩家的箱子打开
  const available = STATE.session.boxes.filter(
    b => !b.opened && b.id !== STATE.session.player_box_id
  );
  if (!available.length) return;
  const box = available[Math.floor(Math.random() * available.length)];
  await openSingleBox(box.id);
}

// ── 报价弹窗 ──────────────────────────────────────────────────
const AI报价文案 = {
  early: '这是个保守参考报价，你可继续探索更多潜力。',
  mid:   '潜力越来越明显，这是目前能评估的最佳报价！',
  late:  '现在的局势对你有利，这是一次难得的提议。',
  final: '最后的机会！这是我们能给出的极限报价。',
};

function getPhaseKey(session) {
  const remaining = session.boxes.filter(b => !b.opened).length;
  if (remaining >= 15) return 'early';
  if (remaining >= 8)  return 'mid';
  if (remaining >= 4)  return 'late';
  return 'final';
}

function estimateGuaranteedTitle(session) {
  if (session.current_round === 0) return '闪电决断者';
  if (session.current_round <= 3) return '精准猎手';
  if (session.current_round >= 5) return '卧龙待醒';
  return '随遇而安者';
}

function showOffer(session) {
  document.getElementById('offer-amount').textContent      = fmt(session.last_offer);
  document.getElementById('offer-ai-message').textContent  = AI报价文案[getPhaseKey(session)];
  document.getElementById('offer-guaranteed-title').textContent =
    `保底称号：${estimateGuaranteedTitle(session)}`;

  const counterBtn = document.getElementById('btn-show-counter');
  counterBtn.disabled    = session.counter_offer_used;
  counterBtn.textContent = session.counter_offer_used
    ? '还价机会已用完' : '还价（剩 1 次机会）';

  const input = document.getElementById('counter-amount');
  input.min   = session.last_offer + 1;
  input.step  = 1;
  input.value = '';
  input.placeholder = `输入还价金额（最少 ${fmt(session.last_offer + 1)}）`;

  toggleHidden('counter-input-area', true);
  showModal('modal-offer');
}

async function acceptOffer() {
  try {
    const data = await API.post(`/api/game/${STATE.sessionId}/accept`);
    STATE.session = data;
    hideModal('modal-offer');
    showSettlement(data, data.title_info);
  } catch (e) {
    alert('操作失败：' + e.message);
  }
}

async function rejectOffer() {
  try {
    const data = await API.post(`/api/game/${STATE.sessionId}/reject`);
    STATE.session = data;
    hideModal('modal-offer');
    if (data.game_over) {
      showSettlement(data);
    } else {
      renderBoxes(data);
      renderValueBoard(data);
      updateProgress(data);
      document.getElementById('btn-continue').disabled = false;
      setAiMessage('继续探索！点击任意箱子或「继续开箱」。');
    }
  } catch (e) {
    alert('操作失败：' + e.message);
  }
}

async function submitCounter() {
  const amount = parseInt(document.getElementById('counter-amount').value, 10);
  const minAmount = STATE.session.last_offer + 1;
  if (!amount || amount < minAmount) {
    alert(`还价金额必须高于当前报价 ${fmt(STATE.session.last_offer)}`);
    return;
  }
  try {
    const data = await API.post(`/api/game/${STATE.sessionId}/counter`, { amount });
    STATE.session = data;
    hideModal('modal-offer');

    if (data.counter_accepted) {
      showSettlement(data, data.title_info);
    } else {
      document.getElementById('counter-result-title').textContent   = '还价未成功 😔';
      document.getElementById('counter-result-message').textContent =
        `AI 交易官拒绝了你的 ${fmt(amount)} 还价。原报价 ${fmt(data.last_offer)} 仍然有效，你可选择接受或继续开箱。`;
      showModal('modal-counter-result');
    }
  } catch (e) {
    alert('操作失败：' + e.message);
  }
}

// ── 结算界面 ──────────────────────────────────────────────────
function showSettlement(session, titleInfo = null) {
  const info = titleInfo || { name: session.final_title, description: '', icon: '🎖️' };
  const isHidden = !!info.hidden;
  const banner = document.querySelector('.title-unlock-banner');
  const label  = document.getElementById('settlement-title-label');
  banner.classList.toggle('hidden-achievement', isHidden);
  label.classList.toggle('hidden-label', isHidden);
  label.textContent = isHidden ? '🔓 隐藏成就解锁' : '新称号解锁';

  document.getElementById('settlement-title-icon').textContent    = info.icon || '🎖️';
  document.getElementById('settlement-title-name').textContent    = info.name || session.final_title;
  document.getElementById('settlement-title-tagline').textContent = info.tagline || '';
  document.getElementById('settlement-title-desc').textContent    = info.description || '';

  const playerBox = session.boxes.find(b => b.id === session.player_box_id);
  document.getElementById('settle-box-value').textContent   = playerBox?.value != null ? fmt(playerBox.value) : '—';
  document.getElementById('settle-intuition').textContent   =
    session.intuition_index != null ? `${session.intuition_index} / 100` : '—';
  document.getElementById('settle-negotiation').textContent =
    session.counter_offer_used ? '主动还价' : session.accepted_offer ? '接受报价' : '坚守到底';
  document.getElementById('settle-deal').textContent        =
    session.accepted_offer
      ? `${fmt(session.last_offer)}（报价）`
      : `${playerBox?.value != null ? fmt(playerBox.value) : '—'}（开箱）`;

  updateStats(session);

  // 结算页双列金额榜
  renderValueBoardInto(session, 'value-panel-left-settle', 'value-panel-right-settle');

  show('screen-settlement');
}

function renderValueBoardInto(session, leftId, rightId) {
  const eliminated = new Set(
    session.boxes
      .filter(b => b.opened && b.value !== undefined)
      .map(b => b.value)
  );
  function buildPanel(panelId, values, tier) {
    const panel = document.getElementById(panelId);
    if (!panel) return;
    panel.innerHTML = '';
    values.forEach(v => {
      const el = document.createElement('div');
      el.className = `value-item ${tier}`;
      if (eliminated.has(v)) el.classList.add('eliminated');
      el.textContent = fmtShort(v);
      panel.appendChild(el);
    });
  }
  buildPanel(leftId,  LEFT_VALUES,  'low');
  buildPanel(rightId, RIGHT_VALUES, 'high');
}

// ── 事件绑定 ──────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('btn-start').addEventListener('click', startNewGame);
  document.getElementById('btn-continue').addEventListener('click', handleContinue);
  document.getElementById('btn-accept').addEventListener('click', acceptOffer);
  document.getElementById('btn-reject').addEventListener('click', rejectOffer);
  document.getElementById('btn-play-again').addEventListener('click', () => show('screen-lobby'));

  document.getElementById('btn-show-counter').addEventListener('click', () => {
    toggleHidden('counter-input-area', false);
  });
  document.getElementById('btn-submit-counter').addEventListener('click', submitCounter);
  document.getElementById('btn-counter-result-ok').addEventListener('click', () => {
    hideModal('modal-counter-result');
    showOffer(STATE.session); // 原报价仍有效，重新展示
  });
});
