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

LOGGER = logging.getLogger(__name__)


class WebSocketRpcHandler(UserMixin, tornado.websocket.WebSocketHandler):
    '''
        An rpc to the services exposed to the application
    '''

    clients = []

    @classmethod
    def keep_alive(cls):
        ''' used to ping the client '''
        msg = str(time.time()).encode("utf8")
        LOGGER.debug(msg)
        for client in cls.clients:
            client.ping(msg)

    @classmethod
    def async_broadcast(cls, message):
        ''' used by piko tool to boradcast from queue '''
        for client in cls.clients:
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
        WebSocketRpcHandler.clients.append(self)
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
                "%s %s %s %r", id(self), context.action_id, context.action, kwargs)
            service = self.application.settings["services"].get(context.action)
            if service is None:
                raise Exception("No such action {}".format(context.action))
            result = service.perform(context, **kwargs)
            if isinstance(result, Future):
                IOLoop.current().add_future(result,
                                            callback=functools.partial(self.write_future, service, context))
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
        if isinstance(result, tuple) and isinstance(result[0], self.micro_context):
            context, result = result
            LOGGER.info("got context")
            self._cookies_ = context.cookies
        self.flush_context(context)
        data = {
            "result": result,
            "action": context.action,
            "id": context.action_id
        }
        if context.cookies.get('current_user') != self.current_user:
            setattr(self, '_current_user', context.cookies['current_user'])
            data['cookie_name'] = self.cookie_name
            data['cookie'] = create_signed_value(
                self.application.settings["cookie_secret"],
                self.cookie_name,
                json_encode(self.current_user)).decode("utf-8")
        self.write_message(json_encode(data))

    def write_err(self, context, ex):
        ''' formats an error response '''
        logging.exception(str(ex))
        self.write_message(json_encode({
            "error": str(ex),
            "action": context.action,
            "id": context.action_id
        }))

    def flush_context(self, context):
        ''' after a success broadcast anything in the context '''
        queue = self.application.settings.get("broadcast_queue")
        for signal, message in context.broadcasts:
            data = json_encode({
                "signal": signal,
                "message": message
            })
            if queue:
                queue.post(data)
            else:
                for client in WebSocketRpcHandler.clients:
                    client.write_message(data)

    def on_close(self):
        ''' remove ourselves from the static clients list '''
        WebSocketRpcHandler.clients.remove(self)
        LOGGER.debug("websocket closed %s", self._client_id)
