from pkg_resources import resource_filename  # @UnresolvedImport

from tornado.options import parse_command_line, define, options
import tornado.ioloop
import tornado.web
from blueshed.micro.utils.service import Service
from blueshed.micro.utils.pika_tool import PikaTool
from blueshed.micro.handlers.api_handler import ApiHandler
from blueshed.micro.handlers.logout_handler import LogoutHandler
from blueshed.micro.handlers.websocketrpc import WebSocketRpcHandler
from spddo.mongo.s3.bucket import AWSConfig
from spddo.mongo.s3.s3put_handler import S3PutHandler
from blueshed.micro.utils.mongo_connection import db_init
import logging
import dotenv
import os

from spddo.mongo import control
from spddo.mongo.control.context import Context

define("debug", False, bool, help="run in debug mode")


def make_app():
    db_url = os.getenv(
        "MONGODB_URI", 'mongodb://localhost:27017/zamazz_database')

    db_init(db_url)

    amqp_url = os.getenv("CLOUDAMQP_URL", '')
    if amqp_url:
        queue = PikaTool(amqp_url,
                         WebSocketRpcHandler.async_broadcast)
        queue.connect()
#         tornado.autoreload.add_reload_hook(queue.close_connection)
        logging.info("broadcast_queue {}".format(amqp_url))
    else:
        queue = None

    if options.debug:
        site_path = resource_filename('spddo', "mongo")
    else:
        site_path = resource_filename('spddo.mongo', "dist")

    handlers = [
        (r"/websocket", WebSocketRpcHandler, {
            'origins': ["localhost:8080",
                        "petermac.local:8080",
                        "spddo-chat.herokuapp.com"]
        }),
        (r"/upload", S3PutHandler, {
            's3_config': AWSConfig('AKIAJ3LFZNJ7PVKED43A',
                                   os.getenv('s3_config')),
            'bucket': 'blueshed-blogs'}),
        (r"/api(.*)", ApiHandler),
        (r"/logout", LogoutHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {
            "path": site_path,
            "default_filename": "index.html"
        })
    ]

    return tornado.web.Application(
        handlers,
        services=Service.describe(control),
        broadcast_queue=queue,
        cookie_name='spddo-mongo',
        cookie_secret='-it-was-a-dark-and-mongo-night-',
        ws_url=os.getenv('ws_url', 'ws://petermac.local:8080/websocket'),
        login_url='/api/login',
        micro_context=Context,
        gzip=True,
        debug=options.debug)


def main():
    logging.basicConfig(level=logging.INFO,
                        format="[%(levelname)1.1s %(asctime)s %(process)d %(thread)x  %(module)s:%(lineno)d] %(message)s")
    parse_command_line()

    if os.path.isfile('.env'):
        dotenv.load_dotenv('.env')

    logging.getLogger("blueshed.micro.utils.service").setLevel(logging.WARN)
    logging.getLogger("blueshed.micro.utils.pika_tool").setLevel(logging.WARN)
    port = int(os.getenv("PORT", 8080))
    app = make_app()
    app.listen(port)
    logging.info("listening on port {}".format(port))
    if options.debug:
        logging.info("running in debug mode")
    tornado.ioloop.PeriodicCallback(
        WebSocketRpcHandler.keep_alive, 30000).start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
