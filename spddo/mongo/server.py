from pkg_resources import resource_filename  # @UnresolvedImport
import logging

from tornado.options import define, options
import tornado.ioloop
import tornado.web

from blueshed.micro.orm.mongo_connection import db_init
from blueshed.micro.utils.config import load_config
from blueshed.micro.utils.utils import url_to_ws_origins
from blueshed.micro.utils.service import Service
from blueshed.micro.queue.pika_topic import PikaTopic
from blueshed.micro.web.logout_handler import LogoutHandler
from blueshed.micro.web.token_access_handler import TokenAccessHandler
from blueshed.micro.web.rpc_websocket import RpcWebsocket
from blueshed.micro.web.rpc_handler import RpcHandler

from spddo.mongo import control
from spddo.mongo.control.context import Context

define("DEBUG", False, bool, help="run in debug mode")
define("PORT", 8080, int, help="port to listen on")
define("MONGODB_URI", "mongodb://localhost:27017/zamazz_database",
       help="motor connection string")
define("CLOUDAMQP_URL",
       default="",
       help="rabbitmq url for broadcasting")
define("CORS_URLS",
       default=["http://localhost:8080",
                "http://petermac.local:8080",
                "https://spddo-chat.herokuapp.com"],
       multiple=True,
       help="allow connection from")


def make_app():
    http_origins = options.CORS_URLS
    ws_origins = [url_to_ws_origins(u) for u in http_origins]

    if options.DEBUG:
        site_path = resource_filename('spddo', "mongo")
    else:
        site_path = resource_filename('spddo.mongo', "dist")

    handlers = [
        (r"/websocket", RpcWebsocket, {
            'ws_origins': ws_origins
        }),
        (r"/api(.*)", RpcHandler, {
            'http_origins': http_origins
        }),
        (r"/token_access", TokenAccessHandler, {
            'auth_url': 'http://localhost:8081/api/validate_token.js',
            'service_token': '12345'
        }),
        (r"/logout", LogoutHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {
            "path": site_path,
            "default_filename": "index.html"
        })
    ]
    settings = {
        'services': Service.describe(control),
        'cookie_name': 'spddo-mongo',
        'cookie_secret': '-it-was-a-dark-and-mongo-night-',
        'login_url': '/api/login',
        'micro_context': Context,
        'allow_exception_messages': options.DEBUG,
        'gzip': True,
        'debug': options.DEBUG
    }

    if options.CLOUDAMQP_URL:
        queue = PikaTopic(options.CLOUDAMQP_URL,
                          RpcWebsocket.async_broadcast,
                          'micro-messages')
        queue.connect()
        settings["broadcast_queue"] = queue
        logging.info("broadcast_queue %s", options.CLOUDAMQP_URL)

    db_init(options.MONGODB_URI)

    return tornado.web.Application(handlers, **settings)


def main():
    load_config(".env")
    logging.getLogger("blueshed.micro.utils.service").setLevel(logging.WARN)
    logging.getLogger("blueshed.micro.utils.pika_tool").setLevel(logging.WARN)
    app = make_app()
    app.listen(options.PORT)
    logging.info("listening on port %s", options.PORT)
    if options.DEBUG:
        logging.info("running in debug mode")
    tornado.ioloop.PeriodicCallback(
        RpcWebsocket.keep_alive, 30000).start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
