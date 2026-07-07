from typing import Optional


def is_command(text: Optional[str]) -> bool:
    """True if the message text is a bot command (starts with '/')."""
    return (text or "").startswith("/")


def handle_as_free_message(text: Optional[str]) -> bool:
    """Predicate for the catch-all free-message handler.

    It must NOT claim command messages: telebot dispatches to the first
    matching handler in registration order, and this catch-all is registered
    before the command handlers, so claiming commands would starve them.
    """
    return not is_command(text)
