from pkg_resources import resource_filename  # @UnresolvedImport

from tornado.options import options
import tornado.ioloop
import tornado.web
import logging

from blueshed.micro.orm import db_connection
from blueshed.micro.utils.executor import pool_init_processes
from blueshed.micro.utils.service import Service
from blueshed.micro.orm.orm_utils import heroku_db_url, create_all, Base
from blueshed.micro.utils.utils import url_to_ws_origins
from blueshed.micro.queue.pika_topic import PikaTopic
from blueshed.micro.web.logout_handler import LogoutHandler
from blueshed.micro.web.rpc_websocket import RpcWebsocket
from blueshed.micro.web.rpc_handler import RpcHandler

from spddo.todo import config
from spddo.todo.actions.context import Context
import spddo.todo.actions


def make_app():
    http_origins = options.CORS_URLS
    ws_origins = [url_to_ws_origins(u) for u in http_origins]
    handlers = [
        (r"/api(.*)", RpcHandler, {'http_origins': http_origins}),
        (r"/websocket", RpcWebsocket, {'ws_origins': ws_origins}),
        (r"/logout", LogoutHandler),
        (r'/(.*)', tornado.web.StaticFileHandler, {
            'path': resource_filename('spddo.todo', 'web'),
            'default_filename': 'index.html'
        })

    ]

    settings = {
        'services': Service.describe(spddo.todo.actions),
        'micro_context': Context,
        'cookie_name': 'micro-todo-session',
        'cookie_secret': '-it-was-a-dark-and-spddo-todo-night-',
        'allow_exception_messages': options.DEBUG,
        'gzip': True,
        'debug': options.DEBUG
    }

    db_url = heroku_db_url(options.CLEARDB_DATABASE_URL)
    engine = db_connection.db_init(db_url)
    if options.DEBUG:
        create_all(Base, engine)

    if options.PROC_POOL_SIZE:
        pool_init_processes(options.PROC_POOL_SIZE,
                            options.DEBUG)

    if options.CLOUDAMQP_URL:
        queue = PikaTopic(options.CLOUDAMQP_URL,
                          RpcWebsocket.async_broadcast,
                          'micro-chat')
        queue.connect()
        settings["broadcast_queue"] = queue
        logging.info("broadcast_queue %s", options.CLOUDAMQP_URL)

    return tornado.web.Application(handlers,
                                   **settings)


def main():
    config.load_config(".env")
    logging.basicConfig(level=logging.INFO,
                        format=options.LOG_FORMAT)

    logging.getLogger("blueshed.micro.utils.service").setLevel(logging.WARN)
    logging.getLogger("blueshed.micro.utils.pika_tool").setLevel(logging.WARN)
    app = make_app()
    app.listen(options.PORT)
    logging.info("listening on port %s", options.PORT)
    if options.DEBUG:
        logging.info('running in debug mode')
    tornado.ioloop.PeriodicCallback(
        RpcWebsocket.keep_alive, 30000).start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
