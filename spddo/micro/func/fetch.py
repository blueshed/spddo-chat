from tornado import gen
from tornado.httpclient import AsyncHTTPClient
from blueshed.micro.utils.pool import pool

@pool
@gen.coroutine
def fetch(context:'micro-context', url:str="http://www.blueshed.co.uk") -> str:
    result = yield AsyncHTTPClient().fetch(url)
    return result.body.decode('utf-8')