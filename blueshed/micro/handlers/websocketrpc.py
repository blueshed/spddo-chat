from blueshed.micro.utils.json_utils import dumps as json_encode
from tornado.concurrent import Future
from tornado.escape import json_decode
from tornado.ioloop import IOLoop
import tornado.websocket
import logging
import time
import functools
import urllib
from tornado.web import create_signed_value
from blueshed.micro.handlers.user_mixin import UserMixin
from blueshed.micro.handlers.context_mixin import ContextMixin

LOGGER = logging.getLogger(__name__)


class WebSocketRpcHandler(ContextMixin, UserMixin,
                          tornado.websocket.WebSocketHandler):
    '''
        An rpc to the services exposed to the application
    '''

    @classmethod
    def keep_alive(cls):
        ''' used to ping the client '''
        msg = str(time.time()).encode("utf8")
        LOGGER.debug(msg)
        for client in cls.context_clients:
            client.ping(msg)

    @classmethod
    def async_broadcast(cls, message):
        ''' used by piko tool to boradcast from queue '''
        for client in cls.context_clients:
            client.write_message(message)

    def initialize(self, origins=None):
        ''' use the origins to specify cors connections '''
        super().initialize()
        self._orgins_ = origins
        self._cookies_ = {}

    def check_origin(self, origin):
        ''' checks the origin is in the origins provided at initialization '''
        if self._orgins_:
            parsed_origin = urllib.parse.urlparse(origin)
            LOGGER.debug("websocket %s", parsed_origin)
            return parsed_origin.netloc in self._orgins_
        return super().check_origin(origin)

    def open(self, *args, **kwargs):
        ''' called when open and adds to static list of clients '''
        self.context_clients.append(self)
        self._client_id = self.get_argument("client_id", id(self))
        self.set_nodelay(True)
        self._cookies_['current_user'] = self.current_user
        LOGGER.debug("websocket open %s", self._client_id)

    def on_message(self, message):
        ''' handle an rpc call '''
        id_, action, kwargs = json_decode(message)
        context = self.micro_context(
            self._client_id, id_, action, self._cookies_)
        try:
            LOGGER.info(
                "%s %s %s %r", id(self),
                context.action_id,
                context.action,
                kwargs)
            service = self.settings["services"].get(context.action)
            if service is None:
                raise Exception("No such service {}".format(context.action))
            result = service.perform(context, **kwargs)
            if isinstance(result, Future):
                IOLoop.current().add_future(result,
                    callback=functools.partial(self.write_future,
                                               service,
                                               context))
            else:
                self.write_result(service, context, result)
        except Exception as ex:
            self.write_err(context, ex)

    def write_future(self, service, context, future):
        ''' called by async repsonses '''
        try:
            result = future.result()
            self.write_result(service, context, result)
        except Exception as ex:
            self.write_err(context, ex)

    def write_result(self, service, context, result):
        ''' formats result and checks for user '''
        LOGGER.info("%s = %s", service.name, result)
        if isinstance(result, tuple) and isinstance(result[0],
                                                    self.micro_context):
            context, result = result
            LOGGER.info("got context")
            self._cookies_ = context.cookies
        self.flush_context(context)
        data = {
            "result": result,
            "action": context.action,
            "id": context.action_id
        }
        self.update_result_data(context, data)
        self.write_message(json_encode(data))

    def write_err(self, context, ex):
        ''' formats an error response '''
        logging.exception(str(ex))
        self.write_message(json_encode({
            "error": str(ex),
            "action": context.action,
            "id": context.action_id
        }))

    def on_close(self):
        ''' remove ourselves from the static clients list '''
        self.context_clients.remove(self)
        LOGGER.debug("websocket closed %s", self._client_id)
