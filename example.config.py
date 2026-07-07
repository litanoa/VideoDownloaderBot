import os

token = (os.getenv("BOT_TOKEN") or "").strip()  # telegram token
logs = None  # logs channel id, if none set to None
max_filesize = 50000000  # bytes
output_folder = "/tmp/yt-dlp-telegram"

# Default delivery mode: ask (show buttons) | video | doc
default_mode = (os.getenv("DEFAULT_MODE") or "ask").strip().lower()
if default_mode not in ("ask", "video", "doc"):
    default_mode = "ask"

# Access control
try:
    admin_id = int(os.getenv("ADMIN_ID") or 0)
except ValueError:
    raise RuntimeError("ADMIN_ID must be a numeric Telegram user id.")
if admin_id <= 0:
    raise RuntimeError("ADMIN_ID is not set. Put your numeric Telegram user id into .env.")
allowlist_path = (os.getenv("ALLOWLIST_PATH") or "/data/allowlist.json").strip()
