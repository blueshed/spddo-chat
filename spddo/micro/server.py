from pkg_resources import resource_filename  # @UnresolvedImport

from sqlalchemy.exc import IntegrityError
from tornado.options import options
import tornado.ioloop
import tornado.web
import logging

from blueshed.micro.orm import db_connection
from blueshed.micro.utils.executor import pool_init_processes
from blueshed.micro.utils.service import Service
from blueshed.micro.orm.orm_utils import heroku_db_url, create_all, Base
from blueshed.micro.utils.utils import url_to_ws_origins
from blueshed.micro.web.logout_handler import LogoutHandler
from blueshed.micro.web.rpc_websocket import RpcWebsocket
from blueshed.micro.web.rpc_handler import RpcHandler
from blueshed.micro.queue.pika_topic import PikaTopic


from spddo.micro.func.context import Context
from spddo.micro.api_page_handler import ApiPageHandler
from spddo.micro.index_handler import IndexHandler
from spddo.micro.func import model
from spddo.micro import config
import spddo.micro.func


def make_app():
    http_origins = options.CORS_URLS
    ws_origins = [url_to_ws_origins(u) for u in http_origins]
    handlers = [
        (r"/api(.*)", RpcHandler, {'http_origins': http_origins,
                                   'ws_url': options.WS_URL}),
        (r"/websocket", RpcWebsocket, {'ws_origins': ws_origins}),
        (r"/logout", LogoutHandler),
        (r"/api.html", ApiPageHandler),
        (r"/", IndexHandler),
    ]

    settings = {
        'services': Service.describe(spddo.micro.func),
        'micro_context': Context,
        'cookie_name': 'micro-session',
        'cookie_secret': '-it-was-a-dark-and-spddo-chat-night-',
        'template_path': resource_filename('spddo.micro', "templates"),
        'allow_exception_messages': options.DEBUG,
        'gzip': True,
        'debug': options.DEBUG
    }

    db_url = heroku_db_url(options.CLEARDB_DATABASE_URL)
    db_connection.db_init(db_url)
    if options.DEBUG:
        create_all(Base, db_connection._engine_)
        with db_connection.session() as session:
            try:
                session.add(model.Person(email="pete@spddo.co.uk",
                                         password="admin"))
                session.commit()
            except IntegrityError:
                session.rollback()

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

    spddo.micro.func.cache.init_mc()

    return tornado.web.Application(handlers, **settings)


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
