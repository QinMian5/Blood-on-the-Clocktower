from __future__ import annotations

"""核心数据模型定义。

这一层主要通过 dataclass 对房间、玩家、投票等实体进行建模，
方便在服务层内以 Python 对象的形式操作，并在接口层再序列化为 JSON。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, List, Optional


class Phase(str, Enum):
    LOBBY = "lobby"
    NIGHT = "night"
    DAY = "day"
    VOTE = "vote"
    RESOLVE = "resolve"
    DAY_END = "day_end"


class LifeStatus(str, Enum):
    """玩家生存状态枚举。"""

    ALIVE = "alive"
    FAKE_DEAD_VOTE = "fake_dead_vote"
    FAKE_DEAD_NO_VOTE = "fake_dead_no_vote"
    DEAD_VOTE = "dead_vote"
    DEAD_NO_VOTE = "dead_no_vote"


@dataclass
class PlayerState:
    id: str
    room_id: str
    name: str
    seat: int
    is_alive: bool = True
    role_id: str | None = None
    joined_at: datetime = field(default_factory=datetime.utcnow)
    is_host: bool = False
    user_id: int | None = None
    ghost_vote_used: bool = False
    is_bot: bool = False
    role_attachments: list["RoleAttachment"] = field(default_factory=list)
    life_status: LifeStatus = LifeStatus.ALIVE
    note: str = ""


@dataclass
class VoteRecord:
    id: str
    room_id: str
    day: int
    nomination_id: str
    nominee_seat: int
    voter_seat: int
    player_id: str
    value: bool
    ts: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ActionRecord:
    id: str
    room_id: str
    night: int
    actor_seat: int
    action_type: str
    target: int | None
    payload: dict[str, Any]
    resolved: bool = False
    ts: datetime = field(default_factory=datetime.utcnow)


@dataclass
class NominationRecord:
    id: str
    room_id: str
    day: int
    nominee_seat: int
    nominator_seat: int
    ts: datetime = field(default_factory=datetime.utcnow)
    confirmed: bool = False
    vote_started: bool = False
    vote_completed: bool = False
    manual_vote_total: int | None = None


@dataclass
class LogEntry:
    id: str
    room_id: str
    ts: datetime
    kind: str
    payload: dict[str, Any]


@dataclass
class RoomState:
    id: str
    code: str
    join_code: str
    script_id: str
    phase: Phase
    created_at: datetime
    host_player_id: str
    day: int = 0
    night: int = 0
    assignments_seed: str | None = None
    players: dict[str, PlayerState] = field(default_factory=dict)
    nominations: list[NominationRecord] = field(default_factory=list)
    votes: list[VoteRecord] = field(default_factory=list)
    actions: list[ActionRecord] = field(default_factory=list)
    logs: list[LogEntry] = field(default_factory=list)
    pending_assignments: dict[int, "RoleAssignment"] = field(default_factory=dict)
    game_result: str | None = None
    vote_session: Optional["VoteSessionState"] = None
    executions: list["ExecutionRecord"] = field(default_factory=list)

    def next_seat(self) -> int:
        if not self.players:
            return 1
        return max(player.seat for player in self.players.values()) + 1

    def list_players(self) -> list[PlayerState]:
        return sorted(self.players.values(), key=lambda player: player.seat)

    def player_by_seat(self, seat: int) -> PlayerState | None:
        for player in self.players.values():
            if player.seat == seat:
                return player
        return None


@dataclass
class ScriptRole:
    id: str
    name: str
    team: str
    tags: list[str] = field(default_factory=list)
    meta: dict[str, Any] = field(default_factory=dict)
    # name_localized 允许以语言代码为 key 存储多国语言名称，
    # 例如 {"zh_CN": "洗衣妇"}，以满足用户希望看到中文角色名的需求。
    name_localized: dict[str, str] = field(default_factory=dict)


@dataclass
class Script:
    id: str
    name: str
    version: str
    roles: list[ScriptRole]
    team_distribution: dict[int, dict[str, int]] = field(default_factory=dict)
    rules: dict[str, Any] = field(default_factory=dict)


@dataclass
class RoleAttachment:
    """表示附带角色（如酒鬼误以为的身份、恶魔伪装等）。"""

    slot: str
    index: int
    role_id: str


@dataclass
class RoleAssignment:
    """房间中的角色分配结果，包含主身份和附带身份。"""

    role_id: str
    attachments: list[RoleAttachment] = field(default_factory=list)


@dataclass
class VoteSessionState:
    """记录当前投票的轮次进度。"""

    nomination_id: str
    order: List[str]
    current_index: int = 0
    finished: bool = False
    votes: dict[str, bool] = field(default_factory=dict)

    def current_player_id(self) -> str | None:
        if self.finished or self.current_index >= len(self.order):
            return None
        return self.order[self.current_index]


@dataclass
class ExecutionRecord:
    """记录每日处决结果，便于前端展示。"""

    day: int
    nominee_seat: int | None
    executed_seat: int | None
    votes_for: int
    alive_count: int
    nomination_id: str | None = None
    target_dead: bool | None = None
    ts: datetime = field(default_factory=datetime.utcnow)
