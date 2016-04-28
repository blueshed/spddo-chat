from pkg_resources import resource_filename  # @UnresolvedImport

from tornado.options import parse_command_line, define, options
import tornado.autoreload
import tornado.ioloop
import tornado.web
import logging
import os

from concurrent.futures.process import ProcessPoolExecutor
from blueshed.micro.utils import db_connection, executor
from blueshed.micro.utils.service import Service
from blueshed.micro.utils.orm_utils import heroku_db_url, create_all, Base
from blueshed.micro.handlers.logout_handler import LogoutHandler
from blueshed.micro.handlers.rpc_websocket import RpcWebsocket
from blueshed.micro.handlers.rpc_handler import RpcHandler
from blueshed.micro.utils.pika_topic import PikaTopic

from spddo.micro.func.context import Context
from spddo.micro.api_page_handler import ApiPageHandler
from spddo.micro.index_handler import IndexHandler
import spddo.micro.func

define('debug', False, bool, help='run in debug mode')
define("db_url",
       default='mysql://root:root@localhost:8889/test',
       help="database url")
define("db_pool_recycle", 60, int,
       help="how many seconds to recycle db connection")
define("proc_pool_size", 0, int,
       help="how processes in the pool")


def make_app():
    db_url = heroku_db_url(os.getenv("CLEARDB_DATABASE_URL",
                                     options.db_url))
    db_connection.db_init(db_url)
    if options.debug:
        create_all(Base, db_connection._engine_)

    pool_size = int(os.getenv("POOL_SIZE", options.proc_pool_size))
    if pool_size:
        micro_pool = ProcessPoolExecutor(pool_size)
        executor.pool_init(micro_pool)
        logging.info("process pool {}".format(pool_size))
        if options.debug:
            tornado.autoreload.add_reload_hook(micro_pool.shutdown)

    amqp_url = os.getenv("CLOUDAMQP_URL", '')
    if amqp_url:
        queue = PikaTopic(amqp_url,
                          RpcWebsocket.async_broadcast,
                          'micro-chat')
        queue.connect()
        logging.info("broadcast_queue {}".format(amqp_url))
    else:
        queue = None

    template_path = resource_filename('spddo.micro', "templates")

    return tornado.web.Application([
        (r"/websocket", RpcWebsocket,
         {'origins': ["localhost:8080", "spddo-chat.herokuapp.com"]}),
        (r"/api.html", ApiPageHandler),
        (r"/api(.*)", RpcHandler),
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
        allow_exception_messages=options.debug,
        gzip=True,
        debug=options.debug)


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
    if options.debug:
        logging.info('running in debug mode')
    tornado.ioloop.PeriodicCallback(
        RpcWebsocket.keep_alive, 30000).start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
