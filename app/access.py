import json
import os
import threading
from typing import Optional


def parse_user_id(text: str) -> Optional[int]:
    """Extract the first integer argument from a command like '/allow 222'."""
    parts = (text or "").split()
    if len(parts) < 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


class AllowList:
    """Persistent Telegram user allow-list with a fixed admin.

    Backed by a JSON file (a list of int user ids). The admin is always allowed
    and cannot be removed. All mutations are written atomically.
    """

    def __init__(self, path: str, admin_id: int):
        self._path = path
        self._admin_id = int(admin_id)
        self._ids: set[int] = set()
        self._lock = threading.Lock()

    def load(self) -> None:
        ids = {self._admin_id}
        try:
            with open(self._path, encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, list):
                ids.update(int(x) for x in data)
        except (FileNotFoundError, ValueError, TypeError):
            pass  # missing or corrupt -> seed with admin only
        self._ids = ids
        self._save()

    def is_admin(self, user_id: int) -> bool:
        return int(user_id) == self._admin_id

    def is_allowed(self, user_id: int) -> bool:
        return int(user_id) in self._ids

    def allow(self, user_id: int) -> bool:
        user_id = int(user_id)
        with self._lock:
            if user_id in self._ids:
                return False
            self._ids.add(user_id)
            self._save()
            return True

    def deny(self, user_id: int) -> bool:
        user_id = int(user_id)
        with self._lock:
            if user_id == self._admin_id or user_id not in self._ids:
                return False
            self._ids.discard(user_id)
            self._save()
            return True

    def users(self) -> list[int]:
        return sorted(self._ids)

    def _save(self) -> None:
        tmp = f"{self._path}.tmp"
        d = os.path.dirname(self._path)
        if d:
            os.makedirs(d, exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(sorted(self._ids), f)
        os.replace(tmp, self._path)
