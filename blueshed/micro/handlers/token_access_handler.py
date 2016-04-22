from tornado import gen
from tornado.escape import json_encode
from tornado.web import RequestHandler, HTTPError
from tornado.httpclient import AsyncHTTPClient
from urllib.parse import urlencode, urlparse
import logging


class TokenAccessHandler(RequestHandler):
    '''
        Validates a token with an auth server and
        puts the result into our access control cookie
        and redirects.
    '''

    def initialize(self, service_token, auth_url):
        self.service_token = service_token
        self.auth_url = auth_url
        o = urlparse(auth_url)
        self._origins_ = ["{}://{}".format(o.scheme, o.netloc)]

    @property
    def cookie_name(self):
        return self.application.settings.get('cookie_name')

    def check_origin(self):
        ''' checks the origin is in the origins provided at initialization '''
        if self._origins_:
            o = urlparse(self.request.headers.get("Referer"))
            logging.info(o)
            origin = "{}://{}".format(o.scheme, o.netloc)
            if origin in self._origins_:
                return origin
            raise HTTPError(403, "Cross origin websockets not allowed")

    def prepare(self):
        RequestHandler.set_default_headers(self)
        if self._origins_:
            self.set_header('Access-Control-Allow-Origin', self.check_origin())
            self.set_header('Access-Control-Allow-Methods', 'GET')
            self.set_header('Access-Control-Max-Age', 1000)
            self.set_header('Access-Control-Allow-Headers', '*')
            self.set_header('Access-Control-Allow-Credentials', 'true')

    def options(self, *args, **kwargs):
        self.finish()

    @gen.coroutine
    def get(self):
        token = self.get_argument("v")
        logging.info("auth token %s", token)
        try:
            args = {
                "token": token,
                "service_token": self.service_token
            }
            result = yield AsyncHTTPClient().fetch(self.auth_url,
                                                   method="POST",
                                                   body=urlencode(args))
            logging.info(result.body)
            self.set_secure_cookie(self.cookie_name, result.body)
            self.write({'result': "ok"})
        except Exception as ex:
            logging.exception(ex)
            self.write({"error": str(ex)})
        finally:
            self.finish()
