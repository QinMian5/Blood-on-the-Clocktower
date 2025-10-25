"""注册码管理。"""

from __future__ import annotations

from pathlib import Path
from threading import Lock


class RegistrationCodeStore:
    """使用本地文本文件管理一次性注册码。"""

    def __init__(self, file_path: Path) -> None:
        self._file_path = file_path
        self._file_path.parent.mkdir(parents=True, exist_ok=True)
        if not self._file_path.exists():
            self._file_path.write_text("", encoding="utf-8")
        self._lock = Lock()

    def consume(self, code: str) -> bool:
        """检查并移除指定注册码，成功时返回 True。"""

        if not code:
            return False
        with self._lock:
            codes = self._load_codes()
            if code not in codes:
                return False
            codes.remove(code)
            self._save_codes(codes)
            return True

    def restore(self, code: str) -> None:
        """在注册失败时恢复先前扣除的注册码。"""

        if not code:
            return
        with self._lock:
            codes = self._load_codes()
            if code not in codes:
                codes.append(code)
                codes.sort()
                self._save_codes(codes)

    def _load_codes(self) -> list[str]:
        data = self._file_path.read_text(encoding="utf-8")
        codes = [
            line.strip()
            for line in data.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        return codes

    def _save_codes(self, codes: list[str]) -> None:
        content = "\n".join(sorted(set(codes)))
        if content:
            content += "\n"
        self._file_path.write_text(content, encoding="utf-8")
