from pkg_resources import resource_filename  # @UnresolvedImport

from tornado.options import parse_command_line, define, options
import tornado.ioloop
import tornado.web
from blueshed.micro.utils import db_connection, orm_utils
from blueshed.micro.utils.service import Service
from blueshed.micro.handlers.api_handler import ApiHandler
from blueshed.micro.handlers.logout_handler import LogoutHandler
from blueshed.micro.handlers.websocketrpc import WebSocketRpcHandler
import logging
import dotenv
import os

from spddo.auth import actions
from spddo.auth.actions.context import Context
from spddo.auth.login_handler import LoginHandler

define('debug', False, bool, help='run in debug mode')
define("db_url", default='mysql://root:root@localhost:8889/auth',
       help="database url")
define("db_pool_recycle", 60, int,
       help="how many seconds to recycle db connection")


def make_app():
    db_url = orm_utils.heroku_db_url(
        os.getenv('CLEARDB_DATABASE_URL',
                  options.db_url))

    db_connection.db_init(db_url,
                          db_pool_recycle=options.db_pool_recycle)
    orm_utils.create_all(orm_utils.Base, db_connection._engine_)

    handlers = [
        (r'/websocket', WebSocketRpcHandler, {
            'origins': ['localhost:8081',
                        'petermac.local:8081']
        }),
        (r'/api(.*)', ApiHandler),
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
        ws_url=os.getenv('ws_url', 'ws://localhost:8081/websocket'),
        login_url='/api/login',
        micro_context=Context,
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
        WebSocketRpcHandler.keep_alive, 30000).start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == '__main__':
    main()
