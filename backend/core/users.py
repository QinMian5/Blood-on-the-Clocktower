"""轻量的玩家账户存储。"""

from __future__ import annotations

import hashlib
import hmac
import secrets
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional


@dataclass(slots=True)
class User:
    """数据库中的玩家账户信息。"""

    id: int
    username: str
    nickname: str
    can_create_room: bool
    is_admin: bool
    created_at: datetime


def _generate_salt() -> str:
    return secrets.token_hex(16)


def _hash_password(password: str, salt: str) -> str:
    return hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), bytes.fromhex(salt), 100_000).hex()


class UserStore:
    """基于 SQLite 的玩家账户存储。"""

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._initialize()

    def _initialize(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    salt TEXT NOT NULL,
                    nickname TEXT NOT NULL,
                    can_create_room INTEGER NOT NULL DEFAULT 0,
                    is_admin INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL
                )
                """
            )
            # 兼容旧版本数据库，确保新增列存在。
            try:
                conn.execute("ALTER TABLE users ADD COLUMN is_admin INTEGER NOT NULL DEFAULT 0")
            except sqlite3.OperationalError:
                pass

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self._db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def create_user(
        self,
        username: str,
        password: str,
        *,
        nickname: Optional[str] = None,
        can_create_room: bool = False,
    ) -> User:
        if not username:
            raise ValueError("用户名不能为空")
        if not password:
            raise ValueError("密码不能为空")
        nickname = nickname or username
        now = datetime.utcnow().isoformat()
        salt = _generate_salt()
        password_hash = _hash_password(password, salt)
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    """
                    INSERT INTO users (
                        username,
                        password_hash,
                        salt,
                        nickname,
                        can_create_room,
                        is_admin,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, 0, ?)
                    """,
                    (username, password_hash, salt, nickname, int(can_create_room), now),
                )
                user_id = cursor.lastrowid
        except sqlite3.IntegrityError as exc:  # pragma: no cover - sqlite error mapping
            raise ValueError("用户名已存在") from exc
        return self.get_user_by_id(user_id)

    def get_user_by_id(self, user_id: int | None) -> User:
        if user_id is None:
            raise ValueError("用户不存在")
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        if row is None:
            raise ValueError("用户不存在")
        return self._row_to_user(row)

    def get_user_by_username(self, username: str) -> User | None:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        if row is None:
            return None
        return self._row_to_user(row)

    def authenticate(self, username: str, password: str) -> User | None:
        record = self._get_user_record(username)
        if record is None:
            return None
        expected_hash = _hash_password(password, record["salt"])
        if hmac.compare_digest(expected_hash, record["password_hash"]):
            return self._row_to_user(record)
        return None

    def _get_user_record(self, username: str) -> sqlite3.Row | None:
        with self._connect() as conn:
            return conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()

    def _row_to_user(self, row: sqlite3.Row) -> User:
        return User(
            id=int(row["id"]),
            username=row["username"],
            nickname=row["nickname"],
            can_create_room=bool(row["can_create_room"]),
            is_admin=bool(row["is_admin"]),
            created_at=datetime.fromisoformat(row["created_at"]),
        )

    def list_users(self, search: str | None = None, *, limit: int = 100) -> list[User]:
        query = "SELECT * FROM users"
        params: list[object] = []
        if search:
            query += " WHERE username LIKE ?"
            params.append(f"%{search}%")
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [self._row_to_user(row) for row in rows]

    def update_user_permissions(
        self,
        user_id: int,
        *,
        can_create_room: bool | None = None,
        is_admin: bool | None = None,
    ) -> User:
        if can_create_room is None and is_admin is None:
            return self.get_user_by_id(user_id)
        updates: list[str] = []
        params: list[object] = []
        if can_create_room is not None:
            updates.append("can_create_room = ?")
            params.append(int(can_create_room))
        if is_admin is not None:
            updates.append("is_admin = ?")
            params.append(int(is_admin))
        params.append(user_id)
        with self._connect() as conn:
            cursor = conn.execute(
                f"UPDATE users SET {', '.join(updates)} WHERE id = ?",
                params,
            )
            if cursor.rowcount == 0:
                raise ValueError("用户不存在")
        return self.get_user_by_id(user_id)
