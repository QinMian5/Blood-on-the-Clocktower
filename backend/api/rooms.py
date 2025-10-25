from __future__ import annotations

"""房间相关 REST API。

接口返回的数据已经包含中文角色名，前端可直接展示。
"""

from fastapi import APIRouter, Depends, HTTPException, status

from backend.core.models import LifeStatus, Phase, RoleAssignment, RoleAttachment
from backend.core.service import AuthorizationError, RoomPrincipal, RoomService
from backend.core.users import UserStore
from backend.schemas.rooms import (
    ActionRequest,
    AssignRolesRequest,
    CreateRoomRequest,
    CreateRoomResponse,
    ExportResponse,
    GameResultRequest,
    JoinRoomRequest,
    JoinRoomResponse,
    NominationRequest,
    NominationTotalRequest,
    PhaseChangeRequest,
    ScriptListItem,
    PlayerNoteRequest,
    PlayerStatusRequest,
    UpdateSeatRequest,
    VoteRequest,
    ExecutionRequest,
)
from backend.security.auth import (
    AuthenticatedUser,
    create_token,
    principal_dependency,
    user_dependency,
)
from backend.ws.rooms import RoomWebSocketManager


def create_rooms_router(
    room_service: RoomService, ws_manager: RoomWebSocketManager, user_store: UserStore
) -> APIRouter:
    router = APIRouter(prefix="/api/rooms", tags=["rooms"])
    # principal_dep 提供基于房间的鉴权依赖，减少重复代码。
    principal_dep = principal_dependency(room_service)
    require_user = user_dependency(user_store)

    @router.post("", response_model=CreateRoomResponse)
    async def create_room(
        payload: CreateRoomRequest,
        current_user: AuthenticatedUser = Depends(require_user),
    ) -> CreateRoomResponse:
        if not current_user.user.can_create_room:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="没有创建房间的权限")
        host_name = payload.host_name or current_user.user.nickname
        room = room_service.create_room(
            host_name,
            host_user_id=current_user.user.id,
            script_id=payload.script_id,
        )
        host_token = create_token(
            room.id,
            player_id=room.host_player_id,
            seat=0,
            role="host",
        )
        return CreateRoomResponse(
            room_id=room.id,
            join_code=room.join_code,
            room_code=room.code,
            host_token=host_token,
        )

    @router.get("/scripts", response_model=list[ScriptListItem])
    async def list_scripts(
        current_user: AuthenticatedUser = Depends(require_user),
    ) -> list[ScriptListItem]:
        if not current_user.user.can_create_room:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="没有创建房间的权限"
            )
        scripts = room_service.list_scripts()
        return [
            ScriptListItem(id=script.id, name=script.name, version=script.version)
            for script in scripts
        ]

    @router.post("/join", response_model=JoinRoomResponse)
    async def join_room_by_code(
        payload: JoinRoomRequest,
        current_user: AuthenticatedUser = Depends(require_user),
    ) -> JoinRoomResponse:
        try:
            room, player = room_service.join_room_by_code(
                payload.code,
                payload.name or current_user.user.nickname,
                user_id=current_user.user.id,
            )
        except AuthorizationError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        player_token = create_token(
            room.id,
            player_id=player.id,
            seat=player.seat,
            role="host" if player.is_host else "player",
        )
        await ws_manager.broadcast_state(room.id)
        return JoinRoomResponse(
            room_id=room.id,
            player_id=player.id,
            seat=player.seat,
            player_token=player_token,
        )

    @router.post("/{room_id}/join", response_model=JoinRoomResponse)
    async def join_room(
        room_id: str,
        payload: JoinRoomRequest,
        current_user: AuthenticatedUser = Depends(require_user),
    ) -> JoinRoomResponse:
        try:
            player = room_service.join_room(
                room_id,
                payload.name or current_user.user.nickname,
                payload.code,
                user_id=current_user.user.id,
            )
        except AuthorizationError as exc:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc
        player_token = create_token(
            room_id,
            player_id=player.id,
            seat=player.seat,
            role="host" if player.is_host else "player",
        )
        await ws_manager.broadcast_state(room_id)
        return JoinRoomResponse(
            room_id=room_id,
            player_id=player.id,
            seat=player.seat,
            player_token=player_token,
        )

    @router.post("/{room_id}/seat")
    async def update_seat(
        room_id: str,
        payload: UpdateSeatRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_same_room(room_id, principal)
        target_player_id = payload.player_id or principal.player_id
        if target_player_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="需要指定玩家")
        if payload.player_id and not principal.is_host:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅主持人可调整其他玩家的座位")
        room = room_service.get_room(room_id)
        if not principal.is_host and room.phase != Phase.LOBBY:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="仅在大厅阶段可自行调整座位"
            )
        try:
            player = room_service.update_player_seat(
                room_id, target_player_id, payload.seat, allow_override=principal.is_host
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {"seat": player.seat}

    @router.get("/{room_id}/state")
    async def get_state(room_id: str, principal: RoomPrincipal = Depends(principal_dep)) -> dict:
        ensure_same_room(room_id, principal)
        # 对不同角色自动脱敏，避免玩家看到不该知道的信息。
        return room_service.snapshot_for(room_id, principal)

    @router.post("/{room_id}/assign")
    async def assign_roles(
        room_id: str,
        payload: AssignRolesRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_host(principal)
        assignment_objects: dict[int, RoleAssignment] | None = None
        if payload.assignments is not None:
            assignment_objects = {
                seat: RoleAssignment(
                    role_id=assignment.role,
                    attachments=[
                        RoleAttachment(slot=att.slot, index=att.index, role_id=att.role_id)
                        for att in (assignment.attachments or [])
                    ],
                )
                for seat, assignment in payload.assignments.items()
            }
        try:
            assignments = room_service.assign_roles(
                room_id,
                seed=payload.seed,
                assignments=assignment_objects,
                finalize=payload.finalize,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {
            "assignments": {
                str(seat): {
                    "role_id": bundle.role_id,
                    "attachments": [
                        {"slot": att.slot, "index": att.index, "role_id": att.role_id}
                        for att in bundle.attachments
                    ],
                }
                for seat, bundle in assignments.items()
            },
            "finalized": payload.finalize,
        }

    @router.post("/{room_id}/phase")
    async def change_phase(
        room_id: str,
        payload: PhaseChangeRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_host(principal)
        try:
            to_phase = Phase(payload.to)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid phase") from exc
        try:
            new_phase = room_service.change_phase(room_id, to_phase)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {"phase": new_phase.value}

    @router.post("/{room_id}/reset")
    async def reset_room(
        room_id: str, principal: RoomPrincipal = Depends(principal_dep)
    ) -> dict:
        ensure_host(principal)
        room_service.reset_room(room_id)
        await ws_manager.broadcast_state(room_id)
        return {"status": "ok"}

    @router.post("/{room_id}/result")
    async def set_game_result(
        room_id: str,
        payload: GameResultRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_host(principal)
        try:
            result = room_service.set_game_result(room_id, payload.result)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {"result": result}

    @router.post("/{room_id}/nominate")
    async def nominate(
        room_id: str,
        payload: NominationRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_same_room(room_id, principal)
        ensure_host(principal)
        try:
            nomination = room_service.add_nomination(
                room_id, payload.nominee_seat, payload.nominator_seat
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {"id": nomination.id}

    @router.post("/{room_id}/nominations/{nomination_id}/start")
    async def start_vote(
        room_id: str,
        nomination_id: str,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_same_room(room_id, principal)
        ensure_host(principal)
        try:
            session = room_service.start_vote(room_id, nomination_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {"nomination_id": session.nomination_id}

    @router.post("/{room_id}/nominations/{nomination_id}/revert")
    async def revert_nomination(
        room_id: str,
        nomination_id: str,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_same_room(room_id, principal)
        ensure_host(principal)
        try:
            room_service.revert_nomination(room_id, nomination_id)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {"status": "ok"}

    @router.post("/{room_id}/nominations/{nomination_id}/total")
    async def update_nomination_total(
        room_id: str,
        nomination_id: str,
        payload: NominationTotalRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_same_room(room_id, principal)
        ensure_host(principal)
        try:
            room_service.update_nomination_total(room_id, nomination_id, payload.total)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {"status": "ok"}

    @router.post("/{room_id}/vote")
    async def vote(
        room_id: str,
        payload: VoteRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_same_room(room_id, principal)
        target_player_id = payload.player_id or principal.player_id
        if target_player_id is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="需要指定玩家")
        if payload.player_id and not principal.is_host:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="仅主持人可代投")
        try:
            vote = room_service.record_vote(
                room_id, payload.nomination_id, target_player_id, payload.value
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {"id": vote.id}

    @router.post("/{room_id}/players/{player_id}/status")
    async def update_player_status(
        room_id: str,
        player_id: str,
        payload: PlayerStatusRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_same_room(room_id, principal)
        ensure_host(principal)
        try:
            status_enum = LifeStatus(payload.status)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="未知状态") from exc
        try:
            player = room_service.set_player_status(room_id, player_id, status_enum)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {"status": player.life_status.value}

    @router.post("/{room_id}/players/{player_id}/note")
    async def update_player_note(
        room_id: str,
        player_id: str,
        payload: PlayerNoteRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_same_room(room_id, principal)
        ensure_host(principal)
        try:
            player = room_service.set_player_note(room_id, player_id, payload.note)
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {"note": player.note}

    @router.post("/{room_id}/execution")
    async def record_execution(
        room_id: str,
        payload: ExecutionRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_same_room(room_id, principal)
        ensure_host(principal)
        try:
            record = room_service.set_execution_result(
                room_id,
                payload.nomination_id,
                payload.executed_seat,
                target_dead=payload.target_dead,
            )
        except ValueError as exc:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
        await ws_manager.broadcast_state(room_id)
        return {
            "day": record.day,
            "nomination_id": record.nomination_id,
            "executed": record.executed_seat,
            "target_dead": record.target_dead,
        }

    @router.post("/{room_id}/action")
    async def night_action(
        room_id: str,
        payload: ActionRequest,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> dict:
        ensure_same_room(room_id, principal)
        if principal.seat is None and not principal.is_host:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Seat required")
        room = room_service.get_room(room_id)
        night = room.night if room.phase == Phase.NIGHT else max(room.night, 1)
        action = room_service.record_action(
            room_id,
            night=night,
            actor_seat=principal.seat or 0,
            action_type=payload.type,
            target=payload.target,
            payload=payload.payload or {},
        )
        await ws_manager.broadcast_state(room_id)
        return {"id": action.id}

    @router.get("/{room_id}/logs", response_model=list[dict])
    async def logs(
        room_id: str,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> list[dict]:
        ensure_host(principal)
        snapshot = room_service.log_export(room_id)
        return snapshot["logs"]

    @router.post("/{room_id}/export", response_model=ExportResponse)
    async def export(
        room_id: str,
        principal: RoomPrincipal = Depends(principal_dep),
    ) -> ExportResponse:
        ensure_host(principal)
        data = room_service.log_export(room_id)
        return ExportResponse(**data)

    return router


def ensure_same_room(room_id: str, principal: RoomPrincipal) -> None:
    if principal.room_id != room_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access to room denied")


def ensure_host(principal: RoomPrincipal) -> None:
    if not principal.is_host:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Host privileges required")
