from app.routing import is_command, handle_as_free_message


def test_slash_prefixed_text_is_a_command():
    assert is_command("/users")
    assert is_command("/allow 222")
    assert is_command("/custom https://x")
    assert is_command("/start")


def test_plain_text_and_urls_are_not_commands():
    assert not is_command("https://instagram.com/reel/abc")
    assert not is_command("hello")
    assert not is_command("")
    assert not is_command(None)


def test_catchall_ignores_commands():
    # The catch-all free-message handler must NOT claim commands, otherwise
    # command handlers registered after it never receive the message.
    assert not handle_as_free_message("/users")
    assert not handle_as_free_message("/allow 222")
    assert not handle_as_free_message("/deny 222")
    assert not handle_as_free_message("/custom https://x")


def test_catchall_handles_normal_messages():
    assert handle_as_free_message("https://instagram.com/reel/abc")
    assert handle_as_free_message("some text with a link")


def test_catchall_handles_non_text_content():
    # photo/video messages have text=None but should still be handled by the
    # free-message handler (it later extracts caption/None safely).
    assert handle_as_free_message(None)
