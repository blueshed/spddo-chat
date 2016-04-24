from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient
from urllib.parse import urlencode

AUTH_URL = "http://localhost:8081/api/"


@coroutine
def sync_auth(method, **kwargs):
    result = yield AsyncHTTPClient().fetch(AUTH_URL + method,
                                           method="POST",
                                           body=urlencode(kwargs))
    return result.body
