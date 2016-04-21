from spddo.subs.actions.save_service import save_service
from spddo.subs.tests.fixtures import context  # @UnusedImport


def test_create_service(context):
    service = save_service(
        context, "service 1", "a testing service", 10, 365)
    assert service['id'] is not None
    assert service['cost'] == 10.0
    assert service['duration'] == 365
    assert service['name'] == "service 1"
    assert service['description'] == "a testing service"


def test_update_service(context):
    service = save_service(
        context, "service 1a", "a testing service!", 11.5, 364, 1)
    assert service['id'] is 1
    assert service['cost'] == 11.5
    assert service['duration'] == 364
    assert service['name'] == "service 1a"
    assert service['description'] == "a testing service!"
