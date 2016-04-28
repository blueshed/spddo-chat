from tornado.web import RequestHandler
from tornado.gen import coroutine
from tornado.httpclient import AsyncHTTPClient
from urllib.parse import urlencode
from blueshed.micro.utils.utils import url_to_cors
from tornado.escape import json_decode
from blueshed.micro.handlers.user_mixin import UserMixin
from blueshed.micro.handlers.cors_mixin import CorsMixin
import logging


class TokenAccessHandler(UserMixin, CorsMixin, RequestHandler):
    '''
        Validates a token with an auth server and
        puts the result into our access control cookie
        and redirects.
    '''

    def initialize(self, service_token, auth_url):
        self.service_token = service_token
        self.auth_url = auth_url
        self._origins_ = [url_to_cors(auth_url)]

    @property
    def origin_whitelist(self):
        return self._origins_

    def options(self, *args, **kwargs):
        self.cors_options(*args, **kwargs)

    @coroutine
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
            message = json_decode(result.body)
            user = message["result"]
            self.set_current_user(user)
            self.write({'result': "ok"})
        except Exception as ex:
            logging.exception(ex)
            self.write({"error": str(ex)})
        finally:
            self.finish()
