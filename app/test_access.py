import json
import threading

import pytest

from app.access import AllowList, parse_user_id


ADMIN = 111
OTHER = 222


def _acl(tmp_path):
    return AllowList(str(tmp_path / "allowlist.json"), admin_id=ADMIN)


def test_seed_creates_list_with_admin(tmp_path):
    acl = _acl(tmp_path)
    acl.load()
    assert acl.is_admin(ADMIN)
    assert acl.is_allowed(ADMIN)
    assert acl.users() == [ADMIN]


def test_other_not_allowed_before_allow(tmp_path):
    acl = _acl(tmp_path)
    acl.load()
    assert not acl.is_allowed(OTHER)
    assert not acl.is_admin(OTHER)


def test_allow_adds_and_persists(tmp_path):
    path = str(tmp_path / "allowlist.json")
    acl = AllowList(path, admin_id=ADMIN)
    acl.load()
    assert acl.allow(OTHER) is True
    assert acl.is_allowed(OTHER)
    # a fresh instance must see the persisted change
    acl2 = AllowList(path, admin_id=ADMIN)
    acl2.load()
    assert acl2.is_allowed(OTHER)


def test_allow_is_idempotent(tmp_path):
    acl = _acl(tmp_path)
    acl.load()
    assert acl.allow(OTHER) is True
    assert acl.allow(OTHER) is False  # already present
    assert acl.users().count(OTHER) == 1  # no duplicates


def test_deny_removes_and_persists(tmp_path):
    path = str(tmp_path / "allowlist.json")
    acl = AllowList(path, admin_id=ADMIN)
    acl.load()
    acl.allow(OTHER)
    assert acl.deny(OTHER) is True
    assert not acl.is_allowed(OTHER)
    acl2 = AllowList(path, admin_id=ADMIN)
    acl2.load()
    assert not acl2.is_allowed(OTHER)


def test_admin_cannot_be_denied(tmp_path):
    acl = _acl(tmp_path)
    acl.load()
    assert acl.deny(ADMIN) is False
    assert acl.is_admin(ADMIN)
    assert acl.is_allowed(ADMIN)


def test_corrupt_json_falls_back_to_seed(tmp_path):
    path = tmp_path / "allowlist.json"
    path.write_text("{ this is not valid json ", encoding="utf-8")
    acl = AllowList(str(path), admin_id=ADMIN)
    acl.load()  # must not raise
    assert acl.is_allowed(ADMIN)
    assert acl.users() == [ADMIN]


def test_persisted_file_is_valid_json(tmp_path):
    path = tmp_path / "allowlist.json"
    acl = AllowList(str(path), admin_id=ADMIN)
    acl.load()
    acl.allow(OTHER)
    data = json.loads(path.read_text(encoding="utf-8"))  # must parse
    assert ADMIN in data
    assert OTHER in data


@pytest.mark.parametrize("text,expected", [
    ("/allow 222", 222),
    ("/deny  333 ", 333),
    ("/allow", None),
    ("/allow abc", None),
    ("/allow 222 444", 222),  # takes first token
    ("/allow -5", None),
])
def test_parse_user_id(text, expected):
    assert parse_user_id(text) == expected


def test_concurrent_allow_is_consistent(tmp_path):
    path = tmp_path / "allowlist.json"
    acl = AllowList(str(path), admin_id=ADMIN)
    acl.load()

    n = 20
    ids = [1000 + i for i in range(n)]
    threads = [threading.Thread(target=acl.allow, args=(uid,)) for uid in ids]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(acl.users()) == n + 1  # + admin
    data = json.loads(path.read_text(encoding="utf-8"))
    assert sorted(data) == acl.users()
