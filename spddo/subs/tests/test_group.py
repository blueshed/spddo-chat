from spddo.subs.actions.save_group import save_group
from spddo.subs.tests.fixtures import context  # @UnusedImport


def test_create_group(context):
    group = save_group(
        context, "group 1")
    assert group['id'] is not None
    assert group['name'] == "group 1"


def test_update_group(context):
    group = save_group(
        context, "group 1a", id=1)
    assert group['id'] is 1
    assert group['name'] == "group 1a"
