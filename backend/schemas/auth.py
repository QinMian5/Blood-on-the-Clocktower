from pydantic import BaseModel, Field


class RegisterRequest(BaseModel):
    username: str = Field(..., pattern=r"^[A-Za-z0-9]{3,32}$", description="仅允许英文与数字")
    password: str = Field(..., min_length=6, max_length=64)
    code: str = Field(..., min_length=4, max_length=64)
    nickname: str | None = Field(None, min_length=1, max_length=64)


class LoginRequest(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    nickname: str
    can_create_room: bool


class LogoutResponse(BaseModel):
    success: bool = True
