import pytest
import tornado.web
from tornado.escape import json_decode
from concurrent.futures.process import ProcessPoolExecutor
from urllib.parse import urlencode

from blueshed.micro.utils.service import Service
from blueshed.micro.handlers.rpc_handler import RpcHandler
from blueshed.micro.utils import db_connection
from spddo.subs.actions.context import Context
from spddo.subs import actions


application = tornado.web.Application([
    (r"/(.*)", RpcHandler),
],
    services=Service.describe(actions),
    context=Context,
    cookie_name='spddo-mongo',
    cookie_secret='-it-was-a-dark-and-mongo-night-',
    pool=ProcessPoolExecutor(4))

db_connection.db_init("mysql+pymysql://root:root@localhost:8889/subs")


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
    assert len(result.get('result')) == 52
