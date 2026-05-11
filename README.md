# 天才交易员

> 一款改编自美国经典电视游戏节目 *Deal or No Deal* 的 H5 手机游戏。
> 靠直觉，赢称号。

**点击[在线试玩](http://genius.xiazq.com/)**
---
## 游戏介绍

26 个神秘箱子，每个箱子里藏着一笔金额（$1 到 $1,000,000）。你先选定自己的箱子，然后一轮轮打开其他箱子缩小范围。每轮结束后，AI 交易官会根据剩余箱子的价值给出浮动报价——接受，还是继续？

你还有一次还价机会。当然，你也可以拒绝所有报价，坚持到最后，打开自己的箱子看看命运给了你什么。

游戏结束时，系统会根据你的整体表现——直觉质量、决策时机、谈判风格——颁发一个专属称号，并附上一段 MBTI 风格的性格解析。

**适合分享朋友圈。**

---

## 功能特性

- **26 个箱子 · 美版金额**：$1 / $2 / $5 … $500,000 / $750,000 / $1,000,000
- **分轮次开箱**：第 1 轮开 6 个，第 2 轮 5 个，逐渐收敛至每轮 1 个
- **AI 浮动报价**：基于剩余均值 × 阶段随机浮动，越到后期报价越高
- **一次还价机会**：只能比报价高，AI 按容忍上限决定接受与否
- **12 种称号 + 2 种隐藏成就**：覆盖所有决策路径，每个都有专属描述
- **Deal or No Deal 风格金额榜**：左栏低档（蓝色）· 右栏高档（金色），实时消除
- **全移动端适配**：max-width 480px，深蓝金色豪华主题

---

## 称号体系

根据**直觉质量**、**接受时机**、**是否还价**综合判定，12 个常规称号 + 2 个隐藏成就：

| 称号 | 触发条件 |
|---|---|
| 🔮 天启交易师 | 直觉指数 ≥ 88 且拒绝所有报价坚持到底 |
| 💎 意志砥柱 | 直觉指数 ≥ 75 且拒绝所有报价 |
| 🎯 精准猎手 | 直觉指数 ≥ 70 且在第 2–4 轮成交 |
| ⚡ 闪电决断者 | 第 1 轮立即接受报价 |
| 🤝 谈判艺术家 | 还价成功 |
| 💡 直觉信徒 | 直觉指数 ≥ 80 且中期成交 |
| 🐉 卧龙待醒 | 直觉指数 ≥ 55 且第 5 轮以后成交 |
| 🎭 戏剧制造者 | 还价被拒，随后接受原报价 |
| 🃏 赌徒哲学家 | 低直觉且拒绝所有报价到底 |
| 🦅 孤胆英雄 | 中等直觉且拒绝所有报价到底 |
| 🌸 淡然成交者 | 低直觉且早期成交 |
| 🌊 随遇而安者 | 兜底称号 |
| 🤑 **百万传奇**（隐藏） | 选中 $1,000,000 箱子并坚持到最后 |
| 💸 **最贵的遗憾**（隐藏） | 选中 $1,000,000 箱子但途中接受了报价 |

---

## 技术栈

| 层 | 技术 |
|---|---|
| 后端框架 | [FastAPI](https://fastapi.tiangolo.com/) |
| 模板引擎 | Jinja2 |
| 服务器 | Uvicorn |
| 前端 | 原生 HTML5 / CSS3 / JavaScript（无框架） |
| 包管理 | [uv](https://docs.astral.sh/uv/) |
| 测试 | pytest + FastAPI TestClient |
| Python | ≥ 3.12 |

游戏状态全部存在服务端内存（以 UUID 会话 ID 为键），无数据库依赖，部署零成本。

---

## 快速开始

### 前置条件

安装 [uv](https://docs.astral.sh/uv/getting-started/installation/)：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 安装与运行

```bash
git clone https://github.com/你的用户名/GeniusTrader.git
cd GeniusTrader

# 安装依赖
uv sync

# 启动开发服务器
uv run uvicorn main:app --reload
```

打开浏览器访问 [http://localhost:8000](http://localhost:8000)

---

## 运行测试

```bash
uv run pytest tests/ -v
```

共 54 个测试，覆盖游戏逻辑、报价计算、称号分配、全部 API 接口。

---

## 项目结构

```
GeniusTrader/
├── main.py                # FastAPI 应用：路由、会话管理、API 接口
├── pyproject.toml
├── app/
│   ├── game.py            # 核心逻辑：箱子生成、开箱、轮次管理
│   ├── offer.py           # 报价计算、还价校验
│   └── titles.py          # 称号体系与直觉指数
├── tests/
│   ├── test_game.py       # 游戏逻辑单元测试
│   ├── test_offer.py      # 报价逻辑单元测试
│   ├── test_titles.py     # 称号分配单元测试
│   └── test_api.py        # API 集成测试
├── templates/
│   └── index.html         # 单页 HTML 框架
└── static/
    ├── css/style.css      # 深蓝金色主题
    └── js/game.js         # 前端状态机与 API 客户端
```

---

## API 概览

| 方法 | 路径 | 说明 |
|---|---|---|
| `POST` | `/api/game/new` | 新建游戏，返回会话 ID 和 26 个箱子 |
| `GET` | `/api/game/{id}/state` | 获取当前游戏状态 |
| `POST` | `/api/game/{id}/select` | 选择玩家箱子 |
| `POST` | `/api/game/{id}/open` | 打开指定箱子 |
| `POST` | `/api/game/{id}/accept` | 接受 AI 报价 |
| `POST` | `/api/game/{id}/reject` | 拒绝 AI 报价，进入下一轮 |
| `POST` | `/api/game/{id}/counter` | 还价（每局限 1 次，且必须高于报价） |

---

## 开源协议

[MIT License](LICENSE)

---

## 致谢

游戏玩法灵感来自美国 NBC 电视节目 *Deal or No Deal*（原版由荷兰节目 *Miljoenenjacht* 改编）。本项目为独立开发的同人实现，与版权方无关联。
