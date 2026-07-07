from app.notify import DenyNotifier, format_access_request


def test_first_attempt_notifies():
    n = DenyNotifier()
    assert n.should_notify(123) is True


def test_repeat_attempt_same_user_is_deduped():
    n = DenyNotifier()
    assert n.should_notify(123) is True
    assert n.should_notify(123) is False
    assert n.should_notify(123) is False


def test_different_users_each_notify_once():
    n = DenyNotifier()
    assert n.should_notify(1) is True
    assert n.should_notify(2) is True
    assert n.should_notify(1) is False
    assert n.should_notify(2) is False


def test_reset_allows_notify_again():
    # when a user is later allowed/denied, admin may want a fresh ping if they return
    n = DenyNotifier()
    n.should_notify(5)
    n.reset(5)
    assert n.should_notify(5) is True


def test_format_with_username():
    msg = format_access_request(user_id=123, username="doctorcandyman", first_name="Jane")
    assert "123" in msg
    assert "doctorcandyman" in msg
    assert "/allow 123" in msg


def test_format_without_username_uses_first_name():
    msg = format_access_request(user_id=456, username=None, first_name="Bob")
    assert "456" in msg
    assert "Bob" in msg
    assert "/allow 456" in msg


def test_format_without_any_name():
    msg = format_access_request(user_id=789, username=None, first_name=None)
    assert "789" in msg
    assert "/allow 789" in msg
