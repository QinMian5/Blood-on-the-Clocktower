from __future__ import annotations

"""游戏记录存储，使用 SQLite 简单持久化每局结算信息。"""

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class GameRecord:
    """数据库中的一条游戏记录。"""

    id: int
    room_id: str
    script_id: str
    result: str
    created_at: datetime
    data: dict[str, Any]


class GameRecordStore:
    """将结算结果保存到 SQLite，便于后续统计或回放。"""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS game_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    room_id TEXT NOT NULL,
                    script_id TEXT NOT NULL,
                    result TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    data TEXT NOT NULL
                )
                """
            )

    def save_record(self, *, room_id: str, script_id: str, result: str, data: dict[str, Any]) -> None:
        payload = json.dumps(data, ensure_ascii=False)
        created_at = datetime.utcnow().isoformat()
        with self._connect() as conn:
            conn.execute(
                "INSERT INTO game_records (room_id, script_id, result, created_at, data) VALUES (?, ?, ?, ?, ?)",
                (room_id, script_id, result, created_at, payload),
            )

    def latest_records(self, limit: int = 20) -> list[GameRecord]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM game_records ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        records: list[GameRecord] = []
        for row in rows:
            records.append(
                GameRecord(
                    id=int(row["id"]),
                    room_id=row["room_id"],
                    script_id=row["script_id"],
                    result=row["result"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    data=json.loads(row["data"]),
                )
            )
        return records
