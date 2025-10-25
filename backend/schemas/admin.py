from datetime import datetime

from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class AdminUserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    can_create_room: bool
    is_admin: bool
    created_at: datetime


class AdminLoginResponse(BaseModel):
    admin: AdminUserResponse


class AdminLogoutResponse(BaseModel):
    success: bool = True


class UpdateUserPermissionsRequest(BaseModel):
    can_create_room: bool | None = None
    is_admin: bool | None = None


class RegistrationCodeCreateRequest(BaseModel):
    count: int = Field(1, ge=1, le=100)


class RegistrationCodeBatchResponse(BaseModel):
    codes: list[str]
