import pytest
import tornado.web
from tornado.escape import json_decode
from tornado.concurrent import DummyExecutor
from concurrent.futures.process import ProcessPoolExecutor
from urllib.parse import urlencode

from blueshed.micro.utils.service import Service
from blueshed.micro.handlers.rpc_handler import RpcHandler
from blueshed.micro.utils import db_connection
from blueshed.micro.utils.orm_utils import drop_all, create_all, Base
from blueshed.tests import actions
from blueshed.tests.actions.context import Context
from blueshed.tests.actions import model


application = tornado.web.Application([
        (r"/(.*)", RpcHandler),
    ],
    services=Service.describe(actions),
    micro_context=Context,
    micro_pool=DummyExecutor(),
#     micro_pool=ProcessPoolExecutor(4),
    cookie_name='blueshed-test',
    cookie_secret='-it-was-a-dark-and-blueshed-night-')


db_connection.db_init("mysql+pymysql://root:root@localhost:8889/test")
with db_connection.session() as session:
    drop_all(session)
create_all(Base, db_connection._engine_)
with db_connection.session() as session:
    session.add(model.User(name="admin", email="admin", password="admin"))
    session.commit()


@pytest.fixture
def app():
    return application


@pytest.mark.gen_test
def test_hello_world_get(http_client, base_url):
    response = yield http_client.fetch(base_url)
    print(response.headers)
    print(response.body)
    assert response.code == 200
    assert response.headers[
        "content-type"] == "application/json; charset=UTF-8"


@pytest.mark.gen_test
def test_hello_world_json(http_client, base_url):
    response = yield http_client.fetch(base_url + "/save_group",
                                       method="POST",
                                       headers={
                                           "content-type": "application/json; charset=UTF-8"
                                       },
                                       body='{ "name": "foobar1" }')
    assert response.code == 200
    assert response.headers[
        "content-type"] == "application/json; charset=UTF-8"
    result = json_decode(response.body)
    print(result)
    assert result.get('result')['name'] == 'foobar1'


@pytest.mark.gen_test
def test_hello_world_plain(http_client, base_url):
    response = yield http_client.fetch(base_url + "/save_group",
                                       method="POST",
                                       body=urlencode({"name": "foobar2"}))
    assert response.code == 200
    assert response.headers[
        "content-type"] == "application/json; charset=UTF-8"
    result = json_decode(response.body)
    print(result)
    assert result.get('result')['name'] == 'foobar2'


@pytest.mark.gen_test
def test_hello_world_login(http_client, base_url):
    response = yield http_client.fetch(base_url + "/login",
                                       method="POST",
                                       body=urlencode({"email": "admin", "password": "admin"}))
    assert response.code == 200
    assert response.headers[
        "content-type"] == "application/json; charset=UTF-8"
    print(dict(response.headers))
    assert response.headers.get("set-cookie").startswith(application.settings['cookie_name'])
    result = json_decode(response.body)
    print(result)
    assert result.get('result')['name'] == 'admin'


@pytest.mark.gen_test
def test_hello_world_filter(http_client, base_url):
    response = yield http_client.fetch(base_url + "/filter_groups",
                                       method="POST",
                                       headers={
                                           "content-type": "application/json; charset=UTF-8"
                                       },
                                       body='{ "term": "foobar" }')
    assert response.code == 200
    assert response.headers[
        "content-type"] == "application/json; charset=UTF-8"
    result = json_decode(response.body)
    print(result)
    assert len(result.get('result')) == 2
