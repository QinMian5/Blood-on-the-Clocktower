"""房间业务逻辑。

RoomService 负责管理房间生命周期、玩家状态、阶段切换等核心流程。
为了方便日后维护与本地化，在关键步骤旁加入中文注释说明操作目的。
"""

from __future__ import annotations

import random
import secrets
import uuid
from collections import Counter, defaultdict
from datetime import datetime
from typing import Any, Iterable

from backend.core.models import (
    ActionRecord,
    ExecutionRecord,
    LifeStatus,
    LogEntry,
    NominationRecord,
    Phase,
    PlayerState,
    RoleAssignment,
    RoleAttachment,
    RoomState,
    Script,
    ScriptRole,
    VoteRecord,
    VoteSessionState,
)
from backend.core.scripts import DEFAULT_SCRIPT, SCRIPTS

TEAM_LABELS = {
    "townsfolk": "镇民",
    "outsider": "外来者",
    "minion": "爪牙",
    "demon": "恶魔",
}

TEAM_DISPLAY_ORDER = ["townsfolk", "outsider", "minion", "demon"]


class RoomNotFoundError(KeyError):
    pass


class AuthorizationError(RuntimeError):
    pass


class RoomService:
    def __init__(self) -> None:
        self._rooms: dict[str, RoomState] = {}

    # Room lifecycle -----------------------------------------------------
    def create_room(
        self, host_name: str, *, host_user_id: int, script_id: str | None = None
    ) -> RoomState:
        # 创建房间时默认加载剧本，并生成主持人与加入验证码。
        script = self._get_script(script_id)
        room_id = uuid.uuid4().hex
        join_code = secrets.token_urlsafe(4)
        access_code = secrets.token_urlsafe(6)
        host_player_id = uuid.uuid4().hex

        room = RoomState(
            id=room_id,
            code=access_code,
            join_code=join_code,
            script_id=script.id,
            phase=Phase.LOBBY,
            created_at=datetime.now(),
            host_player_id=host_player_id,
        )

        # Host is also a player for auditing purposes but does not occupy a seat yet.
        room.players[host_player_id] = PlayerState(
            id=host_player_id,
            room_id=room_id,
            name=host_name,
            seat=0,
            is_host=True,
            user_id=host_user_id,
        )

        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="room_created",
                payload={"script_id": script.id, "host_name": host_name},
            )
        )
        self._rooms[room_id] = room
        return room

    def list_rooms(self) -> Iterable[RoomState]:
        return self._rooms.values()

    def get_room(self, room_id: str) -> RoomState:
        try:
            return self._rooms[room_id]
        except KeyError as exc:  # pragma: no cover - trivial
            raise RoomNotFoundError(room_id) from exc

    # Player management --------------------------------------------------
    def join_room_by_code(
        self, join_code: str, name: str, *, user_id: int | None = None
    ) -> tuple[RoomState, PlayerState]:
        """允许玩家通过加入码进入房间，初始座位号默认为 0。"""

        for room in self._rooms.values():
            if room.join_code == join_code:
                player = self._add_player(room, name, user_id=user_id)
                return room, player
        raise AuthorizationError("Invalid join code")

    def join_room(
        self, room_id: str, name: str, code: str, *, user_id: int | None = None
    ) -> PlayerState:
        """保留原有接口，供主持人面板等通过房间 ID 加入时复用。"""

        room = self.get_room(room_id)
        if code != room.join_code:
            raise AuthorizationError("Invalid join code")
        return self._add_player(room, name, user_id=user_id)

    def update_player_seat(
        self, room_id: str, player_id: str, seat: int, *, allow_override: bool = False
    ) -> PlayerState:
        """玩家或主持人修改座位号，允许重复，仅记录日志并刷新机器人。"""

        room = self.get_room(room_id)
        if seat < 0:
            raise ValueError("座位号不能为负数")
        try:
            player = room.players[player_id]
        except KeyError as exc:
            raise ValueError("玩家不存在") from exc

        if not allow_override and room.phase != Phase.LOBBY:
            raise ValueError("仅在大厅阶段可以自行调整座位")

        player.seat = seat
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="seat_changed",
                payload={"player": player.name, "seat": seat},
            )
        )
        return player

    def _add_player(
        self, room: RoomState, name: str, *, user_id: int | None = None
    ) -> PlayerState:
        player_id = uuid.uuid4().hex
        player_count = sum(1 for existing in room.players.values() if not existing.is_host)
        seat = player_count + 1
        player = PlayerState(
            id=player_id,
            room_id=room.id,
            name=name,
            seat=seat,
            user_id=user_id,
        )
        room.players[player_id] = player
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room.id,
                ts=datetime.now(),
                kind="player_joined",
                payload={"seat": player.seat, "name": name},
            )
        )
        return player

    # Role assignment ----------------------------------------------------
    def assign_roles(
        self,
        room_id: str,
        *,
        seed: str | None = None,
        assignments: dict[int, RoleAssignment] | None = None,
        finalize: bool = False,
    ) -> dict[int, RoleAssignment]:
        room = self.get_room(room_id)
        script = self._get_script(room.script_id)

        if finalize:
            source_assignments = assignments or room.pending_assignments
            if not source_assignments:
                raise ValueError("需要提供最终的角色分配方案")
            validated = self._validate_assignments(
                room, source_assignments, script, require_full=True
            )
            self._ensure_seating_ready(room)
            for player in room.list_players():
                if player.seat <= 0:
                    continue
                bundle = validated.get(player.seat)
                if bundle:
                    player.role_id = bundle.role_id
                    player.role_attachments = [
                        RoleAttachment(slot=att.slot, index=att.index, role_id=att.role_id)
                        for att in bundle.attachments
                    ]
                else:
                    player.role_id = None
                    player.role_attachments = []
            room.pending_assignments = validated
            room.logs.append(
                LogEntry(
                    id=uuid.uuid4().hex,
                    room_id=room_id,
                    ts=datetime.now(),
                    kind="roles_assigned",
                    payload={
                        "seed": room.assignments_seed,
                        "player_roles": {
                            seat: {
                                "role": bundle.role_id,
                                "attachments": [
                                    {
                                        "slot": att.slot,
                                        "index": att.index,
                                        "role": att.role_id,
                                    }
                                    for att in bundle.attachments
                                ],
                            }
                            for seat, bundle in validated.items()
                        },
                    },
                )
            )
            return validated

        if assignments is not None:
            validated = self._validate_assignments(
                room, assignments, script, require_full=False
            )
            seed_value = room.assignments_seed or secrets.token_hex(8)
            if not room.assignments_seed:
                room.assignments_seed = seed_value
            self._auto_fill_attachments(script, validated, random.Random(seed_value))
            room.pending_assignments = validated
            return validated

        generated = self._generate_random_assignments(room, script, seed)
        room.pending_assignments = generated
        return generated

    # Phase transitions --------------------------------------------------
    def change_phase(self, room_id: str, to_phase: Phase) -> Phase:
        room = self.get_room(room_id)
        if room.phase == to_phase:
            return room.phase

        if room.phase == Phase.LOBBY and to_phase != Phase.LOBBY:
            # 游戏从大厅进入正式流程前检查座位合法性，避免重复或跳号。
            self._ensure_seating_ready(room)

        previous = room.phase
        if to_phase != Phase.VOTE:
            room.vote_session = None
        if to_phase == Phase.NIGHT:
            # 首个夜晚记为第 0 夜，之后每次夜晚循环递增。
            if previous == Phase.LOBBY:
                room.day = 0
                # room.night = 0
            elif previous == Phase.DAY:
                room.day -= 1
        elif to_phase == Phase.DAY:
            if previous == Phase.NIGHT:
                room.day += 1
        elif to_phase == Phase.LOBBY:
            room.day = 0
            # room.night = 0
        if previous == Phase.NIGHT and room.day == 0 and to_phase == Phase.RESOLVE:
            to_phase = Phase.LOBBY
        room.phase = to_phase

        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="phase_changed",
                payload={"to": to_phase.value, "day": room.day, "night": room.night},
            )
        )
        return room.phase

    def reset_room(self, room_id: str) -> RoomState:
        room = self.get_room(room_id)
        room.phase = Phase.LOBBY
        room.day = 1
        room.night = 0
        room.assignments_seed = None
        room.pending_assignments.clear()
        room.nominations.clear()
        room.votes.clear()
        room.actions.clear()
        room.game_result = None
        room.vote_session = None
        room.executions.clear()

        for player in room.players.values():
            player.is_alive = True
            player.ghost_vote_used = False
            player.life_status = LifeStatus.ALIVE
            player.role_id = None
            player.role_attachments = []

        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="game_reset",
                payload={},
            )
        )
        return room

    def set_game_result(self, room_id: str, result: str | None) -> str | None:
        room = self.get_room(room_id)
        script = self._get_script(room.script_id)
        allowed = {"blue", "red"}
        if script.rules.get("storyteller_win_available"):
            allowed.add("storyteller")
        if result is not None and result not in allowed:
            raise ValueError("不支持的结局选项")
        room.game_result = result
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="game_result_set",
                payload={"result": result},
            )
        )
        return room.game_result

    def set_player_status(
        self, room_id: str, player_id: str, status: LifeStatus
    ) -> PlayerState:
        room = self.get_room(room_id)
        try:
            player = room.players[player_id]
        except KeyError as exc:
            raise ValueError("找不到玩家") from exc

        player.life_status = status
        if status == LifeStatus.ALIVE:
            player.is_alive = True
            player.ghost_vote_used = False
        elif status == LifeStatus.FAKE_DEAD_VOTE:
            player.is_alive = True
            player.ghost_vote_used = False
        elif status == LifeStatus.FAKE_DEAD_NO_VOTE:
            player.is_alive = True
            player.ghost_vote_used = True
        elif status == LifeStatus.DEAD_VOTE:
            player.is_alive = False
            player.ghost_vote_used = False
        elif status == LifeStatus.DEAD_NO_VOTE:
            player.is_alive = False
            player.ghost_vote_used = True

        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="status_changed",
                payload={"player": player.name, "status": status.value},
            )
        )
        return player

    def set_player_note(self, room_id: str, player_id: str, note: str) -> PlayerState:
        room = self.get_room(room_id)
        try:
            player = room.players[player_id]
        except KeyError as exc:
            raise ValueError("找不到玩家") from exc
        player.note = note
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="player_note_updated",
                payload={"player": player.name, "note": note},
            )
        )
        return player

    def add_nomination(self, room_id: str, nominee_seat: int, nominator_seat: int) -> NominationRecord:
        room = self.get_room(room_id)
        current_day_nominations = [n for n in room.nominations if n.day == room.day]
        if len(current_day_nominations) >= 3:
            raise ValueError("当天提名次数已达 3 次上限")
        nominee = room.player_by_seat(nominee_seat)
        nominator = room.player_by_seat(nominator_seat)
        if nominee is None:
            raise ValueError("找不到被提名的玩家")
        if nominator is None:
            raise ValueError("找不到提名者")
        nomination = NominationRecord(
            id=uuid.uuid4().hex,
            room_id=room_id,
            day=room.day,
            nominee_seat=nominee_seat,
            nominator_seat=nominator_seat,
            confirmed=True,
            vote_started=False,
            vote_completed=False,
        )
        room.nominations.append(nomination)
        room.vote_session = None
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="nominated",
                payload={"nominee": nominee_seat, "by": nominator_seat},
            )
        )
        return nomination

    def start_vote(self, room_id: str, nomination_id: str) -> VoteSessionState:
        room = self.get_room(room_id)
        try:
            nomination = next(n for n in room.nominations if n.id == nomination_id)
        except StopIteration as exc:
            raise ValueError("找不到对应的提名记录") from exc
        if nomination.day != room.day:
            raise ValueError("只能对当前日期的提名进行投票")
        order = self._build_vote_order(room, nomination.nominee_seat)
        session = VoteSessionState(nomination_id=nomination_id, order=order)
        session.current_index = 0
        session.finished = False
        session.votes.clear()
        nomination.vote_started = True
        nomination.vote_completed = False
        room.vote_session = session
        room.votes = [vote for vote in room.votes if vote.nomination_id != nomination_id]
        self._advance_vote_session(room, nomination)
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="vote_started",
                payload={"nomination_id": nomination_id},
            )
        )
        return session

    def revert_nomination(self, room_id: str, nomination_id: str) -> None:
        room = self.get_room(room_id)
        index = None
        for idx, nomination in enumerate(room.nominations):
            if nomination.id == nomination_id:
                index = idx
                break
        if index is None:
            raise ValueError("找不到需要撤销的提名")
        nomination = room.nominations.pop(index)
        room.votes = [vote for vote in room.votes if vote.nomination_id != nomination_id]
        if room.vote_session and room.vote_session.nomination_id == nomination_id:
            room.vote_session = None
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="nomination_reverted",
                payload={"nomination_id": nomination_id},
            )
        )

    def update_nomination_total(self, room_id: str, nomination_id: str, total: int | None) -> None:
        room = self.get_room(room_id)
        try:
            nomination = next(n for n in room.nominations if n.id == nomination_id)
        except StopIteration as exc:
            raise ValueError("找不到对应的提名记录") from exc
        nomination.manual_vote_total = total
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="nomination_total_updated",
                payload={"nomination_id": nomination_id, "total": total},
            )
        )

    def record_vote(
        self,
        room_id: str,
        nomination_id: str,
        player_id: str,
        value: bool,
        *,
        auto: bool = False,
    ) -> VoteRecord:
        room = self.get_room(room_id)
        session = room.vote_session
        if session is None or session.nomination_id != nomination_id:
            raise ValueError("当前没有进行中的投票")
        try:
            nomination = next(n for n in room.nominations if n.id == nomination_id)
        except StopIteration as exc:
            raise ValueError("找不到对应的提名记录") from exc
        if nomination.day != room.day:
            raise ValueError("只能对当前日期的提名进行投票")
        if session.finished:
            raise ValueError("本次投票已经结束")
        expected_player_id = session.current_player_id()
        if expected_player_id != player_id:
            raise ValueError("尚未轮到该玩家投票")
        player = room.players.get(player_id)
        if player is None:
            raise ValueError("找不到玩家")
        if not self._player_can_vote(player) and value:
            raise ValueError("该玩家当前没有投赞成票的权利")
        vote = self._apply_vote(room, nomination, session, player, value, auto=auto)
        if not auto:
            self._advance_vote_session(room, nomination)
        return vote

    def record_action(
        self,
        room_id: str,
        night: int,
        actor_seat: int,
        action_type: str,
        target: int | None,
        payload: dict[str, Any],
    ) -> ActionRecord:
        room = self.get_room(room_id)
        # 夜晚行动统一记录，payload 里可保存剧本特定的详细数据。
        action = ActionRecord(
            id=uuid.uuid4().hex,
            room_id=room_id,
            night=night,
            actor_seat=actor_seat,
            action_type=action_type,
            target=target,
            payload=payload,
        )
        room.actions.append(action)
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="action_recorded",
                payload={
                    "night": night,
                    "actor": actor_seat,
                    "type": action_type,
                    "target": target,
                },
            )
        )
        return action

    # Snapshots ----------------------------------------------------------
    def snapshot_for(self, room_id: str, principal: RoomPrincipal) -> dict[str, Any]:
        room = self.get_room(room_id)
        # snapshot_for 是所有前端视图数据的来源，保持只读纯函数便于测试。
        return build_snapshot(room, principal)

    def log_export(self, room_id: str) -> dict[str, Any]:
        room = self.get_room(room_id)
        return {
            "room": {
                "id": room.id,
                "script_id": room.script_id,
                "phase": room.phase.value,
                "day": room.day,
                "night": room.night,
            },
            "logs": [
                {
                    "id": log.id,
                    "ts": log.ts.isoformat(),
                    "kind": log.kind,
                    "payload": log.payload,
                }
                for log in room.logs
            ],
        }

    # Helpers ------------------------------------------------------------
    def _generate_random_assignments(
        self, room: RoomState, script: Script, seed: str | None
    ) -> dict[int, RoleAssignment]:
        players = [player for player in room.list_players() if player.seat > 0]
        if not players:
            raise ValueError("至少需要一名玩家才能分配角色")
        if len(script.roles) < len(players):
            raise ValueError("剧本中角色数量不足，无法覆盖所有玩家")

        seed_value = seed or secrets.token_hex(8)
        prng = random.Random(seed_value)
        room.assignments_seed = seed_value

        roles = list(script.roles)
        team_counts = self._resolve_team_counts(script, len(players))
        roles_by_team: dict[str, list[ScriptRole]] = defaultdict(list)
        for role in roles:
            roles_by_team[role.team].append(role)
        for bucket in roles_by_team.values():
            prng.shuffle(bucket)

        selected_roles: list[ScriptRole] = []
        for team, count in team_counts.items():
            available = roles_by_team.get(team, [])
            if len(available) < count:
                raise ValueError(f"剧本中 {team} 阵营的角色数量不足")
            selected_roles.extend(available[:count])
            roles_by_team[team] = available[count:]

        if len(selected_roles) < len(players):
            remaining_needed = len(players) - len(selected_roles)
            leftovers: list[ScriptRole] = []
            for bucket in roles_by_team.values():
                leftovers.extend(bucket)
            if len(leftovers) < remaining_needed:
                raise ValueError("剧本角色数量不足，无法满足所有玩家")
            prng.shuffle(leftovers)
            selected_roles.extend(leftovers[:remaining_needed])

        prng.shuffle(selected_roles)
        assigned: dict[int, RoleAssignment] = {}
        for player, role in zip(players, selected_roles):
            assigned[player.seat] = RoleAssignment(role_id=role.id)

        self._auto_fill_attachments(script, assigned, prng)
        return assigned

    def _resolve_team_counts(self, script: Script, player_count: int) -> dict[str, int]:
        if not script.team_distribution:
            teams = Counter(role.team for role in script.roles)
            return dict(teams)
        if player_count in script.team_distribution:
            return dict(script.team_distribution[player_count])
        sorted_keys = sorted(script.team_distribution)
        fallback_key = None
        for key in reversed(sorted_keys):
            if key <= player_count:
                fallback_key = key
                break
        if fallback_key is None:
            fallback_key = sorted_keys[0]
        return dict(script.team_distribution[fallback_key])

    def _auto_fill_attachments(
        self,
        script: Script,
        assignments: dict[int, RoleAssignment],
        prng: random.Random,
    ) -> None:
        role_by_id = {role.id: role for role in script.roles}
        pool = self._build_attachment_pool(script, assignments)
        for bundle in assignments.values():
            role = role_by_id.get(bundle.role_id)
            if not role:
                continue
            slots = role.meta.get("attachment_slots", [])
            for slot_def in slots:
                if not isinstance(slot_def, dict):
                    continue
                slot_id = slot_def.get("id")
                if not slot_id:
                    continue
                count = int(slot_def.get("count", 1))
                allow_duplicates = bool(slot_def.get("allow_duplicates", False))
                team_filter = slot_def.get("team_filter")
                for index in range(count):
                    existing = next(
                        (
                            att
                            for att in bundle.attachments
                            if att.slot == slot_id and att.index == index
                        ),
                        None,
                    )
                    if existing:
                        continue
                    candidate_id = self._pick_attachment_candidate(
                        prng, pool, role_by_id, team_filter, allow_duplicates
                    )
                    if candidate_id is None:
                        continue
                    bundle.attachments.append(
                        RoleAttachment(slot=slot_id, index=index, role_id=candidate_id)
                    )
        for bundle in assignments.values():
            bundle.attachments.sort(key=lambda item: (item.slot, item.index))

    def _build_attachment_pool(
        self, script: Script, assignments: dict[int, RoleAssignment]
    ) -> defaultdict[str, list[str]]:
        role_by_id = {role.id: role for role in script.roles}
        pool: defaultdict[str, list[str]] = defaultdict(list)
        base_ids = {bundle.role_id for bundle in assignments.values()}
        for role in script.roles:
            if role.id in base_ids:
                continue
            pool[role.team].append(role.id)

        for bundle in assignments.values():
            for attachment in bundle.attachments:
                attached_role = role_by_id.get(attachment.role_id)
                if not attached_role:
                    continue
                team_roles = pool.get(attached_role.team)
                if team_roles and attachment.role_id in team_roles:
                    team_roles.remove(attachment.role_id)
        return pool

    def _pick_attachment_candidate(
        self,
        prng: random.Random,
        pool: defaultdict[str, list[str]],
        role_by_id: dict[str, ScriptRole],
        team_filter: list[str] | None,
        allow_duplicates: bool,
    ) -> str | None:
        if team_filter:
            candidates = [role_id for team in team_filter for role_id in pool.get(team, [])]
        else:
            candidates = [role_id for roles in pool.values() for role_id in roles]
        if not candidates:
            return None
        role_id = prng.choice(candidates)
        if not allow_duplicates:
            role = role_by_id.get(role_id)
            if role:
                team_roles = pool.get(role.team)
                if team_roles and role_id in team_roles:
                    team_roles.remove(role_id)
        return role_id

    def _validate_assignments(
        self,
        room: RoomState,
        assignments: dict[int, RoleAssignment],
        script: Script,
        *,
        require_full: bool,
    ) -> dict[int, RoleAssignment]:
        role_by_id = {role.id: role for role in script.roles}
        validated: dict[int, RoleAssignment] = {}
        for seat, bundle in assignments.items():
            player = room.player_by_seat(seat)
            if not player:
                raise ValueError(f"找不到座位 {seat} 的玩家")
            if bundle.role_id not in role_by_id:
                raise ValueError(f"未知角色 ID {bundle.role_id}")
            role = role_by_id[bundle.role_id]
            slot_defs = {
                slot_def["id"]: slot_def
                for slot_def in role.meta.get("attachment_slots", [])
                if isinstance(slot_def, dict) and slot_def.get("id")
            }
            attachments_by_slot: dict[str, dict[int, str]] = defaultdict(dict)
            for attachment in bundle.attachments:
                if attachment.slot not in slot_defs:
                    raise ValueError(
                        f"角色 {role.name} 不支持 {attachment.slot} 附加槽"
                    )
                slot_def = slot_defs[attachment.slot]
                count = int(slot_def.get("count", 1))
                if attachment.index < 0 or attachment.index >= count:
                    raise ValueError(
                        f"{role.name} 的 {attachment.slot} 序号超出允许范围"
                    )
                if attachment.role_id not in role_by_id:
                    raise ValueError(f"未知角色 ID {attachment.role_id}")
                allowed_teams = slot_def.get("team_filter")
                if allowed_teams:
                    attached_role = role_by_id[attachment.role_id]
                    if attached_role.team not in allowed_teams:
                        raise ValueError(
                            f"{role.name} 的 {slot_def.get('label', attachment.slot)} 必须选择指定阵营的角色"
                        )
                attachments_by_slot[attachment.slot][attachment.index] = attachment.role_id

            normalized: list[RoleAttachment] = []
            for slot_id, slot_def in slot_defs.items():
                entries = attachments_by_slot.get(slot_id, {})
                count = int(slot_def.get("count", 1))
                allow_duplicates = bool(slot_def.get("allow_duplicates", False))
                missing = [index for index in range(count) if index not in entries]
                if require_full and missing:
                    label = slot_def.get("label", slot_id)
                    raise ValueError(f"{role.name} 缺少 {label} 的选择")
                if not allow_duplicates and len(set(entries.values())) != len(entries.values()):
                    label = slot_def.get("label", slot_id)
                    raise ValueError(f"{role.name} 的 {label} 不能重复")
                for index in range(count):
                    role_id = entries.get(index)
                    if role_id is None:
                        continue
                    normalized.append(
                        RoleAttachment(slot=slot_id, index=index, role_id=role_id)
                    )

            normalized.sort(key=lambda item: (item.slot, item.index))
            validated[seat] = RoleAssignment(role_id=role.id, attachments=normalized)
        return validated

    def _get_script(self, script_id: str | None) -> Script:
        if not script_id:
            return DEFAULT_SCRIPT
        try:
            return SCRIPTS[script_id]
        except KeyError as exc:  # pragma: no cover - defensive
            raise ValueError(f"Unknown script id {script_id}") from exc

    def _ensure_seating_ready(self, room: RoomState) -> None:
        """检查玩家座位是否符合“从 1 起连续递增且无重复”的要求。"""

        seats = [player.seat for player in room.list_players() if not player.is_host]
        if not seats:
            raise ValueError("至少需要一名玩家才能开始游戏")

        sorted_seats = sorted(seats)
        unique_seats = set(sorted_seats)
        if len(sorted_seats) != len(unique_seats):
            raise ValueError("座位号存在重复，无法开始游戏")

        expected = list(range(1, len(sorted_seats) + 1))
        if sorted_seats != expected:
            raise ValueError("座位号必须从 1 开始依次递增，无法开始游戏")

    def _player_can_vote(self, player: PlayerState) -> bool:
        if player.life_status == LifeStatus.ALIVE:
            return True
        if player.life_status == LifeStatus.FAKE_DEAD_VOTE:
            return not player.ghost_vote_used
        if player.life_status == LifeStatus.FAKE_DEAD_NO_VOTE:
            return False
        if player.life_status == LifeStatus.DEAD_VOTE:
            return not player.ghost_vote_used
        return False

    def _build_vote_order(self, room: RoomState, nominee_seat: int) -> list[str]:
        players = [
            player
            for player in room.list_players()
            if player.seat > 0 and not player.is_host
        ]
        if not players:
            return []
        players.sort(key=lambda p: (p.seat, p.joined_at))
        start_index = 0
        for idx, player in enumerate(players):
            if player.seat > nominee_seat:
                start_index = idx
                break
        else:
            start_index = 0
        ordered = players[start_index:] + players[:start_index]
        return [player.id for player in ordered]

    def _apply_vote(
        self,
        room: RoomState,
        nomination: NominationRecord,
        session: VoteSessionState,
        player: PlayerState,
        value: bool,
        *,
        auto: bool,
    ) -> VoteRecord:
        vote = VoteRecord(
            id=uuid.uuid4().hex,
            room_id=room.id,
            day=room.day,
            nomination_id=nomination.id,
            nominee_seat=nomination.nominee_seat,
            voter_seat=player.seat,
            player_id=player.id,
            value=value,
        )
        room.votes.append(vote)
        session.votes[player.id] = value
        session.current_index += 1
        if player.life_status == LifeStatus.DEAD_VOTE and value:
            player.ghost_vote_used = True
            player.life_status = LifeStatus.DEAD_NO_VOTE
        elif player.life_status == LifeStatus.FAKE_DEAD_VOTE and value:
            player.ghost_vote_used = True
            player.life_status = LifeStatus.FAKE_DEAD_NO_VOTE
        if session.current_index >= len(session.order):
            session.finished = True
            nomination.vote_completed = True
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room.id,
                ts=datetime.now(),
                kind="vote_cast",
                payload={
                    "nominee": nomination.nominee_seat,
                    "nomination_id": nomination.id,
                    "voter": player.seat,
                    "value": value,
                    "auto": auto,
                },
            )
        )
        return vote

    def _advance_vote_session(
        self, room: RoomState, nomination: NominationRecord
    ) -> None:
        session = room.vote_session
        if session is None or session.finished:
            return
        while True:
            current_id = session.current_player_id()
            if current_id is None:
                session.finished = True
                nomination.vote_completed = True
                break
            player = room.players.get(current_id)
            if player is None:
                # 玩家不存在时直接跳过
                session.votes[current_id] = False
                session.current_index += 1
                continue
            if self._player_can_vote(player):
                break
            self._apply_vote(room, nomination, session, player, False, auto=True)
            if session.finished:
                break

    def _alive_player_count(self, room: RoomState) -> int:
        count = 0
        for player in room.list_players():
            if player.seat <= 0 or player.is_host:
                continue
            if player.life_status == LifeStatus.ALIVE:
                count += 1
        return count

    def set_execution_result(
        self,
        room_id: str,
        nomination_id: str | None,
        executed_seat: int | None,
        *,
        target_dead: bool | None = None,
    ) -> ExecutionRecord:
        room = self.get_room(room_id)
        nomination = None
        nominee_seat = None
        votes_for = 0
        if nomination_id:
            try:
                nomination = next(n for n in room.nominations if n.id == nomination_id)
            except StopIteration as exc:
                raise ValueError("找不到提名记录") from exc
            nominee_seat = nomination.nominee_seat
            votes_for = sum(
                1 for vote in room.votes if vote.nomination_id == nomination_id and vote.value
            )
        alive_count = self._alive_player_count(room)
        record = ExecutionRecord(
            day=room.day,
            nominee_seat=nominee_seat,
            executed_seat=executed_seat,
            votes_for=votes_for,
            alive_count=alive_count,
            nomination_id=nomination_id,
            target_dead=target_dead,
        )
        room.executions = [rec for rec in room.executions if rec.day != room.day]
        room.executions.append(record)
        room.logs.append(
            LogEntry(
                id=uuid.uuid4().hex,
                room_id=room_id,
                ts=datetime.now(),
                kind="execution_recorded",
                payload={
                    "nomination_id": nomination_id,
                    "executed": executed_seat,
                    "votes_for": votes_for,
                    "alive_count": alive_count,
                    "target_dead": target_dead,
                },
            )
        )
        return record


class RoomPrincipal:
    def __init__(self, room_id: str, player_id: str | None, seat: int | None, is_host: bool) -> None:
        self.room_id = room_id
        self.player_id = player_id
        self.seat = seat
        self.is_host = is_host

    @property
    def role(self) -> str:
        return "host" if self.is_host else "player"


def build_snapshot(room: RoomState, principal: RoomPrincipal) -> dict[str, Any]:
    me_player: PlayerState | None = None
    if principal.player_id:
        me_player = room.players.get(principal.player_id)

    # 构建一个角色索引，便于在快照中返回中文名称。
    script = SCRIPTS.get(room.script_id, DEFAULT_SCRIPT)
    role_catalog = {role.id: role for role in script.roles}

    ordered_players = room.list_players()
    player_count = sum(1 for player in ordered_players if player.seat > 0)

    seat_counts = Counter(player.seat for player in ordered_players if player.seat > 0)
    players_payload = []
    for player in ordered_players:
        entry: dict[str, Any] = {
            "id": player.id,
            "seat": player.seat,
            "name": player.name,
            "is_alive": player.is_alive,
            "me": player.id == (me_player.id if me_player else None),
            "is_host": player.is_host,
            "ghost_vote_used": player.ghost_vote_used,
            "is_bot": player.is_bot,
            "life_status": player.life_status.value,
        }
        entry["visible_status"] = _visible_status(player, principal, me_player)
        entry["ghost_vote_available"] = not player.ghost_vote_used
        if principal.is_host:
            entry["note"] = player.note
        attachments_payload: list[dict[str, Any]] = []
        base_role = role_catalog.get(player.role_id)
        if player.role_attachments:
            if principal.is_host:
                attachments_payload = _attachment_payload(
                    player.role_attachments,
                    role_catalog,
                    base_role=base_role,
                    hide_owner_slots=False,
                )
            elif me_player and player.id == me_player.id:
                attachments_payload = _attachment_payload(
                    player.role_attachments,
                    role_catalog,
                    base_role=base_role,
                    hide_owner_slots=True,
                )
        if principal.is_host:
            entry["role_secret"] = _serialize_role(base_role)
            if attachments_payload:
                entry["role_attachments"] = attachments_payload
        elif me_player and player.id == me_player.id:
            owner_visible = _owner_visible_role(
                base_role,
                player.role_attachments,
                role_catalog,
            )
            entry["role_secret"] = _serialize_role(owner_visible)
            if attachments_payload:
                entry["role_attachments"] = attachments_payload
        players_payload.append(entry)
        if player.seat > 0 and seat_counts[player.seat] > 1:
            entry["seat_conflict"] = True

    votes_by_nomination: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for vote in sorted(room.votes, key=lambda item: item.ts):
        votes_by_nomination[vote.nomination_id].append(
            {
                "voter": vote.voter_seat,
                "player_id": vote.player_id,
                "value": vote.value,
            }
        )

    nominations_payload = [
        {
            "id": nomination.id,
            "day": nomination.day,
            "nominee": nomination.nominee_seat,
            "by": nomination.nominator_seat,
            "ts": nomination.ts.isoformat(),
            "confirmed": nomination.confirmed,
            "vote_started": nomination.vote_started,
            "vote_completed": nomination.vote_completed,
            "votes": votes_by_nomination.get(nomination.id, []),
            "manual_total": nomination.manual_vote_total,
        }
        for nomination in room.nominations
    ]
    snapshot = {
        "room": {
            "id": room.id,
            "phase": room.phase.value,
            "day": room.day,
            "night": room.night,
            "script_id": room.script_id,
            "game_result": room.game_result,
        },
        "players": players_payload,
        "nominations": nominations_payload,
        "script": _script_payload(script, player_count),
    }
    if principal.is_host:
        snapshot["room"]["join_code"] = room.join_code
        if room.pending_assignments:
            snapshot["pending_assignments"] = {
                str(seat): _serialize_assignment(bundle, role_catalog)
                for seat, bundle in sorted(room.pending_assignments.items())
            }
            snapshot["pending_assignments_meta"] = {
                "team_counts": _assignment_team_counts(
                    room.pending_assignments, role_catalog
                )
            }
    if room.vote_session:
        session = room.vote_session
        vote_session_payload = {
            "nomination_id": session.nomination_id,
            "current_player_id": session.current_player_id(),
            "finished": session.finished,
            "order": [],
        }
        for player_id in session.order:
            player = room.players.get(player_id)
            vote_session_payload["order"].append(
                {
                    "player_id": player_id,
                    "seat": player.seat if player else 0,
                    "name": player.name if player else "",
                    "value": session.votes.get(player_id),
                    "can_vote": _can_vote(player),
                }
            )
        snapshot["vote_session"] = vote_session_payload
    if room.executions:
        snapshot["executions"] = [
            {
                "day": record.day,
                "nominee": record.nominee_seat,
                "executed": record.executed_seat,
                "votes_for": record.votes_for,
                "alive_count": record.alive_count,
                "nomination_id": record.nomination_id,
                "target_dead": record.target_dead,
                "ts": record.ts.isoformat(),
            }
            for record in sorted(room.executions, key=lambda item: item.day)
        ]
    return snapshot


def _serialize_assignment(
    bundle: RoleAssignment, role_catalog: dict[str, ScriptRole]
) -> dict[str, Any]:
    base_role = role_catalog.get(bundle.role_id)
    return {
        "role_id": bundle.role_id,
        "role": _serialize_role(base_role),
        "attachments": _attachment_payload(
            bundle.attachments,
            role_catalog,
            base_role=base_role,
            hide_owner_slots=False,
        ),
    }


def _assignment_team_counts(
    assignments: dict[int, RoleAssignment], role_catalog: dict[str, ScriptRole]
) -> dict[str, int]:
    counts: Counter[str] = Counter()
    for bundle in assignments.values():
        role = role_catalog.get(bundle.role_id)
        if role:
            counts[role.team] += 1
    ordered = {team: counts.get(team, 0) for team in TEAM_DISPLAY_ORDER}
    return ordered


def _serialize_role(role: ScriptRole | None) -> dict[str, Any] | None:
    """将角色对象转换为前端可直接展示的结构。"""

    if role is None:
        return None
    return {
        "id": role.id,
        "name": role.name,
        "name_localized": role.name_localized,
        "team": role.team,
        "team_label": TEAM_LABELS.get(role.team),
    }


def _attachment_payload(
    attachments: list[RoleAttachment],
    role_catalog: dict[str, ScriptRole],
    *,
    base_role: ScriptRole | None = None,
    hide_owner_slots: bool = False,
) -> list[dict[str, Any]]:
    slot_defs: dict[str, dict[str, Any]] = {}
    if base_role and base_role.meta:
        slot_defs = {
            slot_def.get("id"): slot_def
            for slot_def in base_role.meta.get("attachment_slots", [])
            if isinstance(slot_def, dict) and slot_def.get("id")
        }

    payload: list[dict[str, Any]] = []
    for attachment in sorted(attachments, key=lambda item: (item.slot, item.index)):
        slot_def = slot_defs.get(attachment.slot)
        if hide_owner_slots and slot_def and slot_def.get("owner_view") == "replace_primary":
            continue
        payload.append(
            {
                "slot": attachment.slot,
                "slot_label": slot_def.get("label") if slot_def else None,
                "index": attachment.index,
                "role_id": attachment.role_id,
                "role": _serialize_role(role_catalog.get(attachment.role_id)),
            }
        )
    return payload


def _owner_visible_role(
    role: ScriptRole | None,
    attachments: list[RoleAttachment],
    role_catalog: dict[str, ScriptRole],
) -> ScriptRole | None:
    if role is None:
        return None
    slots = role.meta.get("attachment_slots", []) if role.meta else []
    for slot_def in slots:
        if not isinstance(slot_def, dict):
            continue
        if slot_def.get("owner_view") != "replace_primary":
            continue
        slot_id = slot_def.get("id")
        if not slot_id:
            continue
        attachment = next(
            (item for item in attachments if item.slot == slot_id and item.index == 0),
            None,
        )
        if attachment:
            return role_catalog.get(attachment.role_id)
    return role


def _visible_status(
    player: PlayerState, principal: RoomPrincipal, me_player: PlayerState | None
) -> str:
    if principal.is_host or (me_player and player.id == me_player.id):
        return player.life_status.value
    if player.life_status == LifeStatus.FAKE_DEAD_VOTE:
        return LifeStatus.DEAD_VOTE.value
    if player.life_status == LifeStatus.FAKE_DEAD_NO_VOTE:
        return LifeStatus.DEAD_NO_VOTE.value
    return player.life_status.value


def _can_vote(player: PlayerState | None) -> bool:
    if player is None:
        return False
    if player.life_status == LifeStatus.ALIVE:
        return True
    if player.life_status == LifeStatus.FAKE_DEAD_VOTE:
        return not player.ghost_vote_used
    if player.life_status == LifeStatus.FAKE_DEAD_NO_VOTE:
        return False
    if player.life_status == LifeStatus.DEAD_VOTE:
        return not player.ghost_vote_used
    return False


def _script_payload(script: Script, player_count: int) -> dict[str, Any]:
    if script.team_distribution:
        if player_count in script.team_distribution:
            team_counts = dict(script.team_distribution[player_count])
        else:
            sorted_keys = sorted(script.team_distribution)
            fallback_key = None
            for key in reversed(sorted_keys):
                if key <= player_count:
                    fallback_key = key
                    break
            if fallback_key is None:
                fallback_key = sorted_keys[0]
            team_counts = dict(script.team_distribution[fallback_key])
    else:
        team_counts = dict(Counter(role.team for role in script.roles))

    team_distribution = {players: dict(counts) for players, counts in script.team_distribution.items()}
    roles_payload = [
        {
            "id": role.id,
            "name": role.name,
            "name_localized": role.name_localized,
            "team": role.team,
            "team_label": TEAM_LABELS.get(role.team),
            "description": role.meta.get("description") if role.meta else None,
            "attachment_slots": role.meta.get("attachment_slots", []) if role.meta else [],
        }
        for role in script.roles
    ]
    return {
        "id": script.id,
        "name": script.name,
        "version": script.version,
        "team_counts": dict(team_counts),
        "team_distribution": team_distribution,
        "roles": roles_payload,
        "rules": dict(script.rules),
    }
