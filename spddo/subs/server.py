from pkg_resources import resource_filename  # @UnresolvedImport

import logging
import dotenv
import os
from concurrent.futures.process import ProcessPoolExecutor
from tornado.options import parse_command_line, define, options
import tornado.ioloop
import tornado.web
import tornado.autoreload
from blueshed.micro.orm import db_connection, orm_utils
from blueshed.micro.utils.executor import pool_init
from blueshed.micro.utils.service import Service
from blueshed.micro.web.logout_handler import LogoutHandler
from blueshed.micro.web.rpc_handler import RpcHandler
from blueshed.micro.web.rpc_websocket import RpcWebsocket

from spddo.subs import actions
from spddo.subs.actions.context import Context
from spddo.subs.model import Base
from blueshed.micro.utils.utils import url_to_ws_origins

define('debug', False, bool, help='run in debug mode')
define("db_url", default='mysql://root:root@localhost:8889/subs',
       help="database url")
define("db_pool_recycle", 60, int,
       help="how many seconds to recycle db connection")


def make_app():
    http_origins = os.getenv("CORS_URLS",
                             ",".join([
                                 "http://localhost:8080",
                             ])).split(",")
    ws_origins = [url_to_ws_origins(u) for u in http_origins]

    db_url = orm_utils.heroku_db_url(
        os.getenv('CLEARDB_DATABASE_URL', options.db_url))

    engine = db_connection.register_db(db_url, [Base])
    if options.debug:
        orm_utils.create_all(Base, engine)

    if options.debug:
        site_path = resource_filename('spddo', 'subs')
    else:
        site_path = resource_filename('spddo.subs', 'dist')

    handlers = [
        (r'/websocket', RpcWebsocket, {
            'ws_origins': ws_origins,
            'ws_url': 'ws://localhost:8080/websocket'}),
        (r'/rpc(.*)', RpcHandler, {'http_origins': http_origins}),
        (r'/logout', LogoutHandler),
        (r'/(.*)', tornado.web.StaticFileHandler, {
            'path': site_path,
            'default_filename': 'index.html'
        })
    ]

    micro_pool = ProcessPoolExecutor(3)
    pool_init(micro_pool)
    if options.debug:
        tornado.autoreload.add_reload_hook(micro_pool.shutdown)

    return tornado.web.Application(
        handlers,
        services=Service.describe(actions),
        broadcast_queue=None,
        cookie_name='spddo-mongo',
        cookie_secret='-it-was-a-dark-and-mongo-night-',
        ws_url=os.getenv('ws_url', 'ws://localhost:8080/websocket'),
        login_url='/api/login',
        micro_context=Context,
        allow_exception_messages=options.debug,
        gzip=True,
        debug=options.debug)


def main():
    logging.basicConfig(level=logging.INFO,
                        format='[%(levelname)1.1s %(asctime)s %(process)d %(thread)x  %(module)s:%(lineno)d] %(message)s')
    parse_command_line()

    if os.path.isfile('.env'):
        dotenv.load_dotenv('.env')

    logging.getLogger('blueshed.micro.utils.service').setLevel(logging.DEBUG)
    logging.getLogger('blueshed.micro.utils.pika_tool').setLevel(logging.WARN)
    port = int(os.getenv('PORT', 8080))
    app = make_app()
    app.listen(port)
    logging.info('listening on port {}'.format(port))
    if options.debug:
        logging.info('running in debug mode')
    tornado.ioloop.PeriodicCallback(
        RpcWebsocket.keep_alive, 30000).start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
