from pkg_resources import resource_filename  # @UnresolvedImport

from tornado.options import parse_command_line, define, options
import tornado.ioloop
import tornado.web
from blueshed.micro.orm import db_connection, orm_utils
from blueshed.micro.utils.service import Service
from blueshed.micro.web.logout_handler import LogoutHandler
from blueshed.micro.web.rpc_websocket import RpcWebsocket
from blueshed.micro.web.rpc_handler import RpcHandler
import logging
import dotenv
import os

from spddo.auth import actions
from spddo.auth.actions.context import Context
from spddo.auth.login_handler import LoginHandler
from spddo.auth.model import Base
from blueshed.micro.utils.utils import url_to_ws_origins

define('debug', False, bool, help='run in debug mode')
define("db_url", default='mysql://root:root@localhost:8889/auth',
       help="database url")
define("db_pool_recycle", 60, int,
       help="how many seconds to recycle db connection")


def make_app():
    http_origins = os.getenv("CORS_URLS",
                             ",".join([
                                      "http://localhost:8081",
                                      ])).split(",")
    ws_origins = [url_to_ws_origins(u) for u in http_origins]

    db_url = orm_utils.heroku_db_url(
        os.getenv('CLEARDB_DATABASE_URL',
                  options.db_url))

    engine = db_connection.register_db(db_url, [Base])
    if options.debug:
        orm_utils.create_all(Base, engine)

    handlers = [
        (r'/websocket', RpcWebsocket, {'ws_origins': ws_origins}),
        (r'/api(.*)', RpcHandler, {'http_origins': http_origins,
                                   'ws_url': 'ws://localhost:8081/websocket' }),
        (r'/logout', LogoutHandler),
        (r'/(.*)', LoginHandler)
    ]

    return tornado.web.Application(
        handlers,
        services=Service.describe(actions),
        broadcast_queue=None,
        template_path=resource_filename('spddo.auth', 'templates'),
        cookie_name='spddo-auth',
        cookie_secret='-it-was-a-dark-and-auth-night-',
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

    logging.getLogger('blueshed.micro.utils.service').setLevel(logging.INFO)
    logging.getLogger('blueshed.micro.utils.pika_tool').setLevel(logging.WARN)
    port = int(os.getenv('PORT', 8081))
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
