from __future__ import annotations

"""账户注册与登录相关 API。"""

from fastapi import APIRouter, Depends, HTTPException, Response, status

from backend.core.registration import RegistrationCodeStore
from backend.core.users import User, UserStore
from backend.schemas.auth import LoginRequest, LogoutResponse, RegisterRequest, UserResponse
from backend.security.auth import (
    AuthenticatedUser,
    create_user_session_token,
    set_session_cookie,
    user_dependency,
)


def _to_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        can_create_room=user.can_create_room,
    )


def create_auth_router(user_store: UserStore, code_store: RegistrationCodeStore) -> APIRouter:
    router = APIRouter(prefix="/api/auth", tags=["auth"])

    require_user = user_dependency(user_store)

    @router.post("/register", response_model=UserResponse)
    async def register(payload: RegisterRequest, response: Response) -> UserResponse:
        if user_store.get_user_by_username(payload.username):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="用户名已存在")
        if not code_store.consume(payload.code):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="注册码无效或已被使用")
        try:
            user = user_store.create_user(
                payload.username,
                payload.password,
                nickname=payload.nickname or payload.username,
            )
        except ValueError as exc:
            code_store.restore(payload.code)
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        token = create_user_session_token(user.id)
        set_session_cookie(response, token)
        return _to_response(user)

    @router.post("/login", response_model=UserResponse)
    async def login(payload: LoginRequest, response: Response) -> UserResponse:
        user = user_store.authenticate(payload.username, payload.password)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        token = create_user_session_token(user.id)
        set_session_cookie(response, token)
        return _to_response(user)

    @router.post("/logout", response_model=LogoutResponse)
    async def logout(response: Response) -> LogoutResponse:
        set_session_cookie(response, "", clear=True)
        return LogoutResponse()

    @router.get("/me", response_model=UserResponse)
    async def me(user: AuthenticatedUser = Depends(require_user)) -> UserResponse:
        return _to_response(user.user)

    return router
