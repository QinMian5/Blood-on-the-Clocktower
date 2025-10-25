"""管理员后台相关 API。"""

from __future__ import annotations

import re
import secrets

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from fastapi.responses import FileResponse

from backend.core.admin_accounts import AdminAccountStore
from backend.core.history import GameRecordStore
from backend.core.registration import RegistrationCodeStore
from backend.core.users import User, UserStore
from backend.schemas.admin import (
    AdminLoginRequest,
    AdminLoginResponse,
    AdminLogoutResponse,
    AdminProfileResponse,
    AdminUserResponse,
    DeleteUserResponse,
    RegistrationCodeBatchResponse,
    RegistrationCodeCreateRequest,
    UpdateUserRequest,
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
        created_at=user.created_at,
    )


def _generate_code() -> str:
    token = secrets.token_urlsafe(6)
    cleaned = re.sub(r"[^A-Za-z0-9]", "", token).upper()
    if len(cleaned) < 8:
        cleaned += secrets.token_hex(4).upper()
    return cleaned[:8]


def create_admin_router(
    user_store: UserStore,
    code_store: RegistrationCodeStore,
    admin_store: AdminAccountStore,
    game_store: GameRecordStore,
) -> APIRouter:
    router = APIRouter(prefix="/api/admin", tags=["admin"])
    require_admin = admin_dependency(admin_store)

    @router.post("/login", response_model=AdminLoginResponse)
    async def admin_login(payload: AdminLoginRequest, response: Response) -> AdminLoginResponse:
        account = admin_store.authenticate(payload.username, payload.password)
        if not account:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="用户名或密码错误")
        token = create_admin_session_token(account.username)
        set_admin_session_cookie(response, token)
        return AdminLoginResponse(admin=AdminProfileResponse(username=account.username))

    @router.post("/logout", response_model=AdminLogoutResponse)
    async def admin_logout(response: Response) -> AdminLogoutResponse:
        set_admin_session_cookie(response, "", clear=True)
        return AdminLogoutResponse()

    @router.get("/me", response_model=AdminProfileResponse)
    async def admin_me(admin: AuthenticatedAdmin = Depends(require_admin)) -> AdminProfileResponse:
        _ = admin
        return AdminProfileResponse(username=admin.account.username)

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
        payload: UpdateUserRequest,
        admin: AuthenticatedAdmin = Depends(require_admin),
    ) -> AdminUserResponse:
        _ = admin
        try:
            user = user_store.update_user_permissions(
                user_id,
                can_create_room=payload.can_create_room,
                nickname=payload.nickname,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return _to_admin_response(user)

    @router.delete("/users/{user_id}", response_model=DeleteUserResponse)
    async def delete_user(
        user_id: int,
        admin: AuthenticatedAdmin = Depends(require_admin),
    ) -> DeleteUserResponse:
        _ = admin
        try:
            user_store.delete_user(user_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
        return DeleteUserResponse()

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

    @router.get("/export/users")
    async def export_users(admin: AuthenticatedAdmin = Depends(require_admin)) -> FileResponse:
        _ = admin
        if not user_store.db_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="用户数据库不存在")
        return FileResponse(
            path=user_store.db_path,
            filename="users.db",
            media_type="application/octet-stream",
        )

    @router.get("/export/games")
    async def export_games(admin: AuthenticatedAdmin = Depends(require_admin)) -> FileResponse:
        _ = admin
        if not game_store.db_path.exists():
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="游戏记录数据库不存在")
        return FileResponse(
            path=game_store.db_path,
            filename="game_records.db",
            media_type="application/octet-stream",
        )

    return router
