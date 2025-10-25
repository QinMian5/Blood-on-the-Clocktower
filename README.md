# Blood on the Clocktower Assistant

An all-in-one companion web application for running and playing online sessions of the social deduction game **Blood on the Clocktower**. The project ships a FastAPI backend plus a Vite + React single-page frontend that keeps the host and players synchronized through REST and WebSocket APIs.

## Getting started

### Prerequisites

- Python 3.11+
- Node.js 20+

### Backend setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn backend.app:app --reload
```

### Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The Vite dev server proxies API calls and WebSocket traffic to the FastAPI backend (`http://localhost:8000`).

### Docker

A multi-stage `deploy/Dockerfile` is provided to build both the frontend assets and backend server. You can run everything with docker-compose:

```bash
cd deploy
docker-compose up --build
```

## Features

- Account registration with invite codes, cookie-based login, and optional host privileges
- Players pick their own seat numbers；主持人需在座位从 1 起连续且无重复时才能开始游戏
- Host-only room creation, join-code sharing, and full role visibility；普通玩家仅能查看自身身份
- Phase management for day/night cycles with vote and nomination history playback
- Role assignment from a localized sample script including中文介绍、阵营分布
- Real-time room state synchronization via WebSockets
- Event log tail（主持人可见）与回放导出支持
- Responsive Tailwind UI tailored for both hosts and players

## Project layout

```
backend/  # FastAPI application
frontend/ # Vite + React SPA
shared/   # Shared type definitions
deploy/   # Containerization assets
```

## How the pieces fit together

- **Frontend ⇄ Backend 通信**：前端页面通过 `frontend/src/api` 下的轻量 fetch 封装访问 FastAPI 提供的 REST 接口（创建房间、加入、切换阶段等），并在 `frontend/src/store/roomStore.ts` 中维护一个 WebSocket 连接接收实时快照。REST 负责初始化数据，WS 持续推送 `snapshot/state_diff` 事件让界面保持同步。
- **前端页面扩展**：所有路由级页面位于 `frontend/src/pages/`。例如首页/注册逻辑集中在 `JoinPage.tsx`，房间面板是 `RoomPage.tsx`。若要扩展 UI，可在 `frontend/src/components/` 添加复用组件，在 `frontend/src/styles.css` 定义样式，并通过 Zustand store (`frontend/src/store`) 共享状态。
- **业务逻辑位置**：核心流程（玩家加入、身份分配、阶段切换、投票记录等）集中在 `backend/core/service.py` 的 `RoomService`。REST 路由位于 `backend/api/rooms.py`，WebSocket 广播在 `backend/ws/rooms.py`。若要修改游戏规则或校验逻辑，可在这些文件及 `backend/core/models.py` 中调整。新的账号系统由 `backend/api/auth.py` + `backend/core/users.py` + `backend/core/registration.py` 提供。
- **剧本与角色**：角色的英文/中文名称与阵营信息集中在 `backend/core/roles.py`，以便多个剧本复用。同一目录下的 `scripts.py` 通过引用这些角色 ID 组装剧本，并维护不同玩家人数对应的阵营配比。要扩展剧本，可新增角色到 `roles.py`，再在 `SCRIPTS` 字典中登记剧本并配置人数曲线。
- **玩家数据库与注册码**：SQLite 数据库存放于 `backend/data/users.db`（路径可配置），初始化时会自动创建。一次性注册码从 `backend/data/registration_codes.txt` 读取，每行一个，注册成功后自动删除。若要追加注册码，直接编辑该文本文件即可，支持 `#` 开头的注释行。

## Environment variables

Environment configuration follows 12-factor practices via:

- `APP_ENV` – runtime environment (`dev` / `prod`)
- `APP_SECRET` – JWT signing secret
- `DB_URL` – database connection string (unused in memory-only MVP)
- `REDIS_URL` – optional Pub/Sub backend (reserved for future use)
- `CORS_ORIGINS` – comma-separated list of allowed origins
- `USER_DB_PATH` – 玩家账户 SQLite 数据库路径（默认 `./backend/data/users.db`）
- `REGISTRATION_CODES_PATH` – 注册码文本文件路径（默认 `./backend/data/registration_codes.txt`）
