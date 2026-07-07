import threading
from typing import Optional


class DenyNotifier:
    """Tracks which denied users the admin has already been pinged about,
    so repeated attempts by the same user don't spam the admin.

    In-memory only: a restart re-pings each returning user once, which is fine
    for an anti-spam guard (restarts are rare, the data isn't valuable).
    """

    def __init__(self):
        self._seen: set[int] = set()
        self._lock = threading.Lock()

    def should_notify(self, user_id: int) -> bool:
        with self._lock:
            if user_id in self._seen:
                return False
            self._seen.add(user_id)
            return True

    def reset(self, user_id: int) -> None:
        with self._lock:
            self._seen.discard(user_id)


def format_access_request(user_id: int, username: Optional[str], first_name: Optional[str]) -> str:
    if username:
        who = f"@{username}"
    elif first_name:
        who = first_name
    else:
        who = f"user {user_id}"
    return (
        f"🔒 Access request from {who} (id {user_id}).\n"
        f"To grant: /allow {user_id}"
    )
