from spddo.auth.tests.fixtures import context  # @UnusedImport
from spddo.auth.actions.save_user import save_user
from spddo.auth.actions.save_service import save_service
from spddo.auth.actions.set_subscriptions import set_subscriptions
from spddo.auth.actions.login import login
from urllib.parse import urlparse, parse_qs
from spddo.auth.actions.validate_token import validate_token


def test_create_user(context):
    user = save_user(
        context, 1, "John Doe", "j.doe@doe.com", "password")
    assert user['id'] is 1
    assert user['email'] == 'j.doe@doe.com'
    assert user['name'] == "John Doe"
    assert 'password' not in user


def test_create_service(context):
    service = save_service(
        context, 1, name="spddo mongo",
        cookie_url="http://locahost:8080/token_access?v={}",
        cors="localhost:8080")
    assert service['id'] is 1
    assert service['name'] == "spddo mongo"

    # put the token in the context for later
    # just for this test
    context.set_cookie('service_token', service["token"])


def test_subscription(context):
    result = set_subscriptions(
        context, user_id=1, service_ids=[1])
    assert result is None


def test_login(context):
    result = login(context, "j.doe@doe.com", "password")
    assert result.get('services')
    print(result)

    # get the token from the result
    o = urlparse(result['services'][0])
    q = parse_qs(o.query)
    token = q.get("v")
    assert token is not None

    # we put the service token in the context earlier
    service_token = context.get_cookie('service_token')
    user = validate_token(context, token, service_token)
    print(user)
    assert user['id'] is 1
    assert user['email'] == 'j.doe@doe.com'
    assert user['name'] == "John Doe"
