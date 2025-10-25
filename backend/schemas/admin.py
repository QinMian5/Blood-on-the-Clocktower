from datetime import datetime

from pydantic import BaseModel, Field


class AdminLoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=64)
    password: str = Field(..., min_length=1, max_length=128)


class AdminAccountResponse(BaseModel):
    username: str


class AdminUserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    can_create_room: bool
    created_at: datetime


class AdminLoginResponse(BaseModel):
    admin: AdminAccountResponse


class AdminLogoutResponse(BaseModel):
    success: bool = True


class AdminProfileResponse(AdminAccountResponse):
    pass


class UpdateUserRequest(BaseModel):
    can_create_room: bool | None = None
    nickname: str | None = Field(default=None, min_length=1, max_length=64)


class DeleteUserResponse(BaseModel):
    success: bool = True


class RegistrationCodeCreateRequest(BaseModel):
    count: int = Field(1, ge=1, le=100)


class RegistrationCodeBatchResponse(BaseModel):
    codes: list[str]
