"""管理员账户存储，从秘密文件中读取。"""

from __future__ import annotations

import hmac
from dataclasses import dataclass
from pathlib import Path
from typing import Dict


@dataclass(slots=True)
class AdminAccount:
    """管理员账户凭证。"""

    username: str
    password: str


class AdminAccountStore:
    """从指定文件加载管理员账号与密码。

    文件格式为每行一个账号，形如 ``用户名:密码``，支持 ``#`` 开头的注释行。
    """

    def __init__(self, secrets_path: Path) -> None:
        self._secrets_path = secrets_path
        self._accounts: Dict[str, AdminAccount] = {}
        self.reload()

    def reload(self) -> None:
        """重新读取密钥文件，便于热更新。"""

        accounts: Dict[str, AdminAccount] = {}
        try:
            raw = self._secrets_path.read_text(encoding="utf-8")
        except FileNotFoundError:
            # 如果文件不存在，则保持为空列表，所有登录都会失败。
            self._accounts = {}
            return
        for line in raw.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if ":" not in stripped:
                continue
            username, password = stripped.split(":", 1)
            username = username.strip()
            password = password.strip()
            if not username or not password:
                continue
            accounts[username] = AdminAccount(username=username, password=password)
        self._accounts = accounts

    def authenticate(self, username: str, password: str) -> AdminAccount | None:
        account = self._accounts.get(username)
        if not account:
            return None
        if hmac.compare_digest(account.password, password):
            return account
        return None

    def get_account(self, username: str) -> AdminAccount:
        account = self._accounts.get(username)
        if not account:
            raise KeyError(username)
        return account

    @property
    def secrets_path(self) -> Path:
        return self._secrets_path

