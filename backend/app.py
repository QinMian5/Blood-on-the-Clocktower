from __future__ import annotations

"""FastAPI 应用入口。"""

from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api.admin import create_admin_router
from backend.api.auth import create_auth_router
from backend.api.rooms import create_rooms_router
from backend.core.config import get_settings
from backend.core.admin_accounts import AdminAccountStore
from backend.core.history import GameRecordStore
from backend.core.registration import RegistrationCodeStore
from backend.core.service import RoomService
from backend.core.users import UserStore
from backend.security.auth import principal_from_token
from backend.ws.rooms import RoomWebSocketManager

settings = get_settings()
user_store = UserStore(Path(settings.user_db_path))
code_store = RegistrationCodeStore(Path(settings.registration_codes_path))
game_store = GameRecordStore(Path(settings.game_db_path))
admin_store = AdminAccountStore(Path(settings.admin_secrets_path))
room_service = RoomService(game_store)
ws_manager = RoomWebSocketManager(room_service)

app = FastAPI(title="Blood on the Clocktower Assistant", version="0.1.0")

if settings.cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(create_auth_router(user_store, code_store))
app.include_router(create_admin_router(user_store, code_store, admin_store, game_store))
app.include_router(create_rooms_router(room_service, ws_manager, user_store))


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


frontend_dist = Path(__file__).resolve().parent.parent / "frontend" / "dist"
if frontend_dist.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="spa")


@app.websocket("/ws/rooms/{room_id}")
async def websocket_endpoint(room_id: str, websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4401)
        return
    try:
        principal = principal_from_token(room_service, token)
    except Exception:  # pragma: no cover - network scenario
        await websocket.close(code=4401)
        return
    if principal.room_id != room_id:
        await websocket.close(code=4403)
        return
    try:
        await ws_manager.handle_client(websocket, principal)
    except WebSocketDisconnect:
        await ws_manager.disconnect(websocket)
