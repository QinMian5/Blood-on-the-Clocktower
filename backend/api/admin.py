"""管理员后台相关 API。"""

from __future__ import annotations

import re
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status

from backend.core.registration import RegistrationCodeStore
from backend.core.users import User, UserStore
from backend.schemas.admin import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminLogoutResponse,
    AdminUserResponse,
    RegistrationCodeBatchResponse,
    RegistrationCodeCreateRequest,
    UpdateUserPermissionsRequest,
)
from backend.security.auth import (
    AuthenticatedAdmin,
    admin_dependency,
    create_admin_session_token,
    set_admin_session_cookie,
)


def _to_admin_response(user: User) -> AdminUserResponse:
    return AdminUserResponse(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        can_create_room=user.can_create_room,
        is_admin=user.is_admin,
        created_at=user.created_at,
    )


def _generate_code() -> str:
    token = secrets.token_urlsafe(6)
    cleaned = re.sub(r"[^A-Za-z0-9]", "", token).upper()
    if len(cleaned) < 8:
        cleaned += secrets.token_hex(4).upper()
    return cleaned[:8]


def create_admin_router(user_store: UserStore, code_store: RegistrationCodeStore) -> APIRouter:
    router = APIRouter(prefix="/api/admin", tags=["admin"])
    require_admin = admin_dependency(user_store)

    @router.post("/login", response_model=AdminLoginResponse)
    async def admin_login(payload: AdminLoginRequest, response: Response) -> AdminLoginResponse:
        user = user_store.authenticate(payload.username, payload.password)
        if not user or not user.is_admin:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        token = create_admin_session_token(user.id)
        set_admin_session_cookie(response, token)
        return AdminLoginResponse(admin=_to_admin_response(user))

    @router.post("/logout", response_model=AdminLogoutResponse)
    async def admin_logout(response: Response) -> AdminLogoutResponse:
        set_admin_session_cookie(response, "", clear=True)
        return AdminLogoutResponse()

    @router.get("/me", response_model=AdminUserResponse)
    async def admin_me(admin: AuthenticatedAdmin = Depends(require_admin)) -> AdminUserResponse:
        return _to_admin_response(admin.user)

    @router.get("/users", response_model=list[AdminUserResponse])
    async def list_users(
        search: str | None = Query(default=None, alias="search"),
        admin: AuthenticatedAdmin = Depends(require_admin),
    ) -> list[AdminUserResponse]:
        _ = admin
        users = user_store.list_users(search)
        return [_to_admin_response(user) for user in users]

    @router.patch("/users/{user_id}", response_model=AdminUserResponse)
    async def update_user(
        user_id: int,
        payload: UpdateUserPermissionsRequest,
        admin: AuthenticatedAdmin = Depends(require_admin),
    ) -> AdminUserResponse:
        _ = admin
        try:
            user = user_store.update_user_permissions(
                user_id,
                can_create_room=payload.can_create_room,
                is_admin=payload.is_admin,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return _to_admin_response(user)

    @router.get("/registration-codes", response_model=RegistrationCodeBatchResponse)
    async def list_codes(admin: AuthenticatedAdmin = Depends(require_admin)) -> RegistrationCodeBatchResponse:
        _ = admin
        codes = code_store.list_codes()
        return RegistrationCodeBatchResponse(codes=codes)

    @router.post("/registration-codes", response_model=RegistrationCodeBatchResponse)
    async def create_codes(
        payload: RegistrationCodeCreateRequest,
        admin: AuthenticatedAdmin = Depends(require_admin),
    ) -> RegistrationCodeBatchResponse:
        _ = admin
        requested = payload.count
        generated: list[str] = []
        attempts = 0
        # 避免极端情况下死循环，这里限制尝试次数。
        while len(generated) < requested and attempts < requested * 10:
            attempts += 1
            code = _generate_code()
            added = code_store.add_codes([code])
            if added:
                generated.extend(added)
        if len(generated) < requested:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="生成注册码失败，请稍后重试")
        return RegistrationCodeBatchResponse(codes=generated)

    return router
