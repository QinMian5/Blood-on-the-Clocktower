from __future__ import annotations

"""WebSocket 管理器，用于实时同步房间状态。"""

import asyncio
from dataclasses import dataclass
from typing import Dict, List

from fastapi import WebSocket, WebSocketDisconnect

from backend.core.service import RoomPrincipal, RoomService


@dataclass
class RoomConnection:
    websocket: WebSocket
    principal: RoomPrincipal


class RoomWebSocketManager:
    def __init__(self, room_service: RoomService) -> None:
        self.room_service = room_service
        self._connections: Dict[str, List[RoomConnection]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, principal: RoomPrincipal) -> None:
        await websocket.accept()
        connection = RoomConnection(websocket=websocket, principal=principal)
        async with self._lock:
            self._connections.setdefault(principal.room_id, []).append(connection)
        # 初次连接立即推送一次完整快照，确保前端状态与服务器同步。
        await self._send_snapshot(connection)

    async def disconnect(self, websocket: WebSocket) -> None:
        async with self._lock:
            for room_id, connections in list(self._connections.items()):
                self._connections[room_id] = [
                    connection for connection in connections if connection.websocket is not websocket
                ]
                if not self._connections[room_id]:
                    self._connections.pop(room_id, None)

    async def broadcast_state(self, room_id: str) -> None:
        connections = await self._connections_for_room(room_id)
        await asyncio.gather(*(self._send_state_diff(connection) for connection in connections), return_exceptions=True)

    async def broadcast_log(self, room_id: str) -> None:
        connections = await self._connections_for_room(room_id)
        await asyncio.gather(*(self._send_log_tail(connection) for connection in connections), return_exceptions=True)

    async def handle_client(self, websocket: WebSocket, principal: RoomPrincipal) -> None:
        try:
            await self.connect(websocket, principal)
            while True:
                message = await websocket.receive_json()
                if message.get("type") == "request_snapshot":
                    await self._send_snapshot(RoomConnection(websocket=websocket, principal=principal))
        except WebSocketDisconnect:
            await self.disconnect(websocket)

    async def _connections_for_room(self, room_id: str) -> List[RoomConnection]:
        async with self._lock:
            return list(self._connections.get(room_id, []))

    async def _send_snapshot(self, connection: RoomConnection) -> None:
        payload = self.room_service.snapshot_for(connection.principal.room_id, connection.principal)
        await connection.websocket.send_json({"type": "snapshot", "data": payload})

    async def _send_state_diff(self, connection: RoomConnection) -> None:
        payload = self.room_service.snapshot_for(connection.principal.room_id, connection.principal)
        await connection.websocket.send_json({"type": "state_diff", "data": payload})

    async def _send_log_tail(self, connection: RoomConnection) -> None:
        payload = self.room_service.snapshot_for(connection.principal.room_id, connection.principal)
        await connection.websocket.send_json({"type": "log", "data": payload.get("log_tail", [])})
