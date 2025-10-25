"""认证与授权相关的辅助函数。"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Callable

import jwt
from fastapi import Cookie, Depends, HTTPException, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from backend.core.config import get_settings
from backend.core.service import RoomPrincipal, RoomService
from backend.core.users import User, UserStore


TOKEN_TTL_MINUTES = 8 * 60
USER_TOKEN_TTL_DAYS = 7
SESSION_COOKIE_NAME = "botc_session"


def create_token(room_id: str, *, player_id: str | None, seat: int | None, role: str) -> str:
    """生成房间作用域的 JWT，供前端持有。"""
    settings = get_settings()
    payload: dict[str, Any] = {
        "room_id": room_id,
        "role": role,
        "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=TOKEN_TTL_MINUTES),
        "iat": datetime.now(tz=timezone.utc),
    }
    if player_id:
        payload["player_id"] = player_id
    if seat is not None:
        payload["seat"] = seat
    return jwt.encode(payload, settings.app_secret, algorithm="HS256")


def decode_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.app_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:  # pragma: no cover - delegated to library
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token") from exc


auth_scheme = HTTPBearer(auto_error=False)


class AuthenticatedPrincipal(RoomPrincipal):
    pass


def principal_dependency(room_service: RoomService):
    async def _get_principal(credentials: HTTPAuthorizationCredentials = Depends(auth_scheme)) -> AuthenticatedPrincipal:
        if not credentials:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing credentials")
        # 将 Authorization 头部转换为房间上下文，供路由处理函数使用。
        return principal_from_token(room_service, credentials.credentials)

    return _get_principal


def principal_from_token(room_service: RoomService, token: str) -> AuthenticatedPrincipal:
    token_data = decode_token(token)
    room_id = token_data.get("room_id")
    if not room_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    player_id = token_data.get("player_id")
    seat = token_data.get("seat")
    role = token_data.get("role")
    if role not in {"host", "player", "spectator"}:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token role")
    is_host = role == "host"
    if player_id:
        room = room_service.get_room(room_id)
        player = room.players.get(player_id)
        if not player:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unknown player")
        seat = player.seat
    return AuthenticatedPrincipal(room_id=room_id, player_id=player_id, seat=seat, is_host=is_host)


class AuthenticatedUser:
    def __init__(self, user: User) -> None:
        self.user = user


def create_user_session_token(user_id: int) -> str:
    settings = get_settings()
    now = datetime.now(tz=timezone.utc)
    payload: dict[str, Any] = {
        "user_id": user_id,
        "exp": now + timedelta(days=USER_TOKEN_TTL_DAYS),
        "iat": now,
    }
    return jwt.encode(payload, settings.app_secret, algorithm="HS256")


def decode_user_session_token(token: str) -> dict[str, Any]:
    settings = get_settings()
    try:
        return jwt.decode(token, settings.app_secret, algorithms=["HS256"])
    except jwt.PyJWTError as exc:  # pragma: no cover - delegated to library
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态失效") from exc


def set_session_cookie(response: Response, token: str, *, clear: bool = False) -> None:
    if clear:
        response.delete_cookie(SESSION_COOKIE_NAME, path="/")
        return
    response.set_cookie(
        SESSION_COOKIE_NAME,
        token,
        max_age=USER_TOKEN_TTL_DAYS * 24 * 60 * 60,
        httponly=True,
        samesite="lax",
        path="/",
    )


def _user_from_token(user_store: UserStore, token: str) -> AuthenticatedUser:
    data = decode_user_session_token(token)
    user_id = data.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态失效")
    try:
        user = user_store.get_user_by_id(int(user_id))
    except ValueError as exc:  # pragma: no cover - defensive
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="登录状态失效") from exc
    return AuthenticatedUser(user)


def user_dependency(user_store: UserStore) -> Callable[[str | None], AuthenticatedUser]:
    async def _dependency(session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> AuthenticatedUser:
        if not session:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="需要先登录")
        return _user_from_token(user_store, session)

    return _dependency


def optional_user_dependency(user_store: UserStore) -> Callable[[str | None], AuthenticatedUser | None]:
    async def _dependency(session: str | None = Cookie(default=None, alias=SESSION_COOKIE_NAME)) -> AuthenticatedUser | None:
        if not session:
            return None
        try:
            return _user_from_token(user_store, session)
        except HTTPException:
            return None

    return _dependency
