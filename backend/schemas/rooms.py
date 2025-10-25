from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CreateRoomRequest(BaseModel):
    host_name: str | None = Field(None, min_length=1, max_length=64)
    script_id: str | None = None


class CreateRoomResponse(BaseModel):
    room_id: str
    join_code: str
    room_code: str
    host_token: str


class JoinRoomRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=64)
    code: str


class JoinRoomResponse(BaseModel):
    room_id: str
    player_id: str
    seat: int
    player_token: str


class UpdateSeatRequest(BaseModel):
    seat: int = Field(..., ge=0, description="玩家可自行选择的座位号，0 表示未选择")
    player_id: str | None = Field(
        None, description="主持人可指定其他玩家的 ID，普通玩家无需填写"
    )


class RoleAttachmentPayload(BaseModel):
    slot: str
    index: int
    role_id: str


class SeatAssignmentPayload(BaseModel):
    role: str
    attachments: list[RoleAttachmentPayload] | None = None


class AssignRolesRequest(BaseModel):
    seed: str | None = None
    assignments: dict[int, SeatAssignmentPayload] | None = None
    finalize: bool = False


class PhaseChangeRequest(BaseModel):
    to: str


class GameResultRequest(BaseModel):
    result: str | None = Field(
        None,
        description="游戏结局，可选 blue/red/storyteller，None 表示清除结果",
    )


class NominationRequest(BaseModel):
    nominee_seat: int
    nominator_seat: int


class NominationTotalRequest(BaseModel):
    total: int | None = Field(
        None,
        description="主持人手动录入的总得票数，None 表示还原为系统统计值",
    )


class VoteRequest(BaseModel):
    nomination_id: str
    value: bool
    player_id: str | None = None


class PlayerStatusRequest(BaseModel):
    status: str = Field(
        ...,
        description="玩家新的状态：alive/fake_dead_vote/fake_dead_no_vote/dead_vote/dead_no_vote",
    )


class PlayerNoteRequest(BaseModel):
    note: str = Field(
        "",
        max_length=512,
        description="主持人记录玩家备注的文本，建议控制在 512 个字符内",
    )


class ExecutionRequest(BaseModel):
    nomination_id: str | None = Field(None, description="对应的提名 ID，可为空表示无人被处决")
    executed_seat: int | None = Field(None, ge=0, description="被处决的座位号，0 或 None 表示无人处决")
    target_dead: bool | None = Field(
        None, description="标记被处决的目标是否死亡，None 表示未记录"
    )


class ActionRequest(BaseModel):
    type: str
    target: int | None = None
    payload: dict[str, Any] | None = None


class ExportResponse(BaseModel):
    room: dict[str, Any]
    logs: list[dict[str, Any]]
