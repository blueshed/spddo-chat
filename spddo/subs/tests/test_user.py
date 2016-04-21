from spddo.subs.actions.save_user import save_user
from spddo.subs.tests.fixtures import context  # @UnusedImport


def test_create_user(context):
    user = save_user(
        context, "John Doe", "j.doe@doe.com", "password")
    assert user['id'] is not None
    assert user['email'] == 'j.doe@doe.com'
    assert user['name'] == "John Doe"
    assert 'password' not in user


def test_update_user(context):
    user = save_user(
        context, name="John P Doe", id=1)
    assert user['id'] is 1
    assert user['email'] == 'j.doe@doe.com'
    assert user['name'] == "John P Doe"
    assert 'password' not in user


def test_update_password(context):
    user = save_user(
        context, password="foo.bar", id=1)
    assert user['id'] is 1
    assert user['email'] == 'j.doe@doe.com'
    assert user['name'] == "John P Doe"
    assert 'password' not in user
