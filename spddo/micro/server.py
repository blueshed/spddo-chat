from pkg_resources import resource_filename  # @UnresolvedImport

from tornado.options import parse_command_line, define, options
import tornado.autoreload
import tornado.ioloop
import tornado.web
from blueshed.micro.utils.service import Service
from blueshed.micro.utils.sql_pool import SQLPool
from blueshed.micro.utils.orm_utils import heroku_db_url
from blueshed.micro.utils.db_connection import db_init
from blueshed.micro.utils.pika_tool import PikaTool
from blueshed.micro.handlers.websocketrpc import WebSocketRpcHandler
from blueshed.micro.handlers.api_handler import ApiHandler
from blueshed.micro.handlers.logout_handler import LogoutHandler
import logging
import os

import spddo.micro.func
from spddo.micro.func.context import Context
from spddo.micro.api_page_handler import ApiPageHandler
from spddo.micro.index_handler import IndexHandler

define('debug', False, bool, help='run in debug mode')
define("db_url", default='sqlite:///', help="database url")
define("db_pool_recycle", 60, int,
       help="how many seconds to recycle db connection")


def make_app():
    db_url = heroku_db_url(os.getenv("CLEARDB_DATABASE_URL",
                                     options.db_url))

    pool_size = int(os.getenv("POOL_SIZE", 0))
    if pool_size:
        pool = SQLPool(spddo.micro.func, pool_size, db_url)
        tornado.autoreload.add_reload_hook(pool.close)
        logging.info("pool_size {}".format(pool_size))
    else:
        db_init(db_url)
        pool = None

    amqp_url = os.getenv("CLOUDAMQP_URL", '')
    if amqp_url:
        queue = PikaTool(amqp_url,
                         WebSocketRpcHandler.async_broadcast)
        queue.connect()
        logging.info("broadcast_queue {}".format(amqp_url))
    else:
        queue = None

    template_path = resource_filename('spddo.micro', "templates")

    return tornado.web.Application([
        (r"/websocket", WebSocketRpcHandler,
         {'origins': ["localhost:8080", "spddo-chat.herokuapp.com"]}),
        (r"/api.html", ApiPageHandler),
        (r"/api(.*)", ApiHandler),
        (r"/logout", LogoutHandler),
        (r"/", IndexHandler),
    ],
        services=Service.describe(spddo.micro.func),
        broadcast_queue=queue,
        micro_context=Context,
        cookie_name='micro-session',
        cookie_secret='-it-was-a-dark-and-spddo-chat-night-',
        ws_url=os.getenv('ws_url', 'ws://localhost:8080/websocket'),
        template_path=template_path,
        gzip=True,
        debug=True)


def main():
    logging.basicConfig(level=logging.INFO,
                        format="[%(levelname)1.1s %(asctime)s %(process)d %(thread)x  %(module)s:%(lineno)d] %(message)s")
    parse_command_line()
    logging.getLogger("micro.utils.service").setLevel(logging.WARN)
    logging.getLogger("micro.utils.pika_tool").setLevel(logging.WARN)
    port = int(os.getenv("PORT", 8080))
    app = make_app()
    app.listen(port)
    logging.info("listening on port {}".format(port))
    tornado.ioloop.PeriodicCallback(
        WebSocketRpcHandler.keep_alive, 30000).start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
