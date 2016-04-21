from spddo.subs.tests.fixtures import context  # @UnusedImport
from spddo.subs.actions.save_service import save_service
from spddo.subs.actions.save_user import save_user
from spddo.subs.actions.save_group import save_group
from spddo.subs.actions.subscribe import subscribe
from spddo.subs.actions.make_payment import make_payment
from spddo.subs.actions.active_subscriptions import active_subscriptions


def test_init(context):
    user = save_user(
        context, "John Doe", "j.doe@doe.com", "password")
    group = save_group(
        context, "group 1")
    service = save_service(
        context, "service 1", "a testing service", 10, 7)
    subscription = subscribe(
        context, user['id'], group['id'], service['id'])

    subs = active_subscriptions(context, user['id'])
    assert len(subs) is 0

    make_payment(
        context, group_id=group['id'])

    for message in context.broadcasts:
        print(message)

    subs = active_subscriptions(context, user['id'])
    assert len(subs) is 1

    assert subs[0]['id'] == subscription['id']

    assert False
