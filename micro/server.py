from tornado.options import parse_command_line
import tornado.autoreload
import tornado.ioloop
import tornado.web
import micro.func
from micro.utils.service import Service
from micro.utils.sql_pool import SQLPool
from micro.utils.orm_utils import heroku_db_url
from micro.utils.db_connection import db_init
from micro.utils.pika_tool import PikaTool
from micro.handlers.websocketrpc import WebSocketRpcHandler
from micro.handlers.api_handler import ApiHandler
from micro.handlers.index_handler import IndexHandler
from micro.handlers.logout_handler import LogoutHandler
import logging
import os


def make_app():
    db_url = heroku_db_url(os.getenv("CLEARDB_DATABASE_URL",
                'mysql://b8bb1b63b5ca04:c7cd499e@eu-cdbr-west-01.cleardb.com/heroku_40e583c01e53bdf?reconnect=true'))
    
    pool_size = int(os.getenv("POOL_SIZE", 1))
    if pool_size:
        pool = SQLPool(pool_size, db_url)
        tornado.autoreload.add_reload_hook(pool.close)
        logging.info("pool_size {}".format(pool_size))
    else:
        db_init(db_url)
        pool = None   
    
    amqp_url = os.getenv("CLOUDAMQP_URL", 'amqp://zypslyni:dEKcw_wXgseQ7SeFbTlrWizuzM3GIV0L@hare.rmq.cloudamqp.com/zypslyni')
    if amqp_url:
        queue = PikaTool(amqp_url, 
                         WebSocketRpcHandler.async_broadcast)
        queue.connect()
        tornado.autoreload.add_reload_hook(queue.close_connection)
        logging.info("broadcast_queue {}".format(amqp_url))
    else:
        queue = None
    
    return tornado.web.Application([
                (r"/websocket", WebSocketRpcHandler,{'origins':["localhost:8080","spddo-chat.herokuapp.com"]}),
                (r"/api(.*)", ApiHandler),
                (r"/logout", LogoutHandler),
                (r"/", IndexHandler),
            ], 
            services=Service.describe(micro.func),
            broadcast_queue=queue,
            cookie_name='micro-session',
            cookie_secret='-it-was-adark-and-stormy-night-',
            ws_url=os.getenv('ws_url','ws://localhost:8080/websocket'),
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
    tornado.ioloop.PeriodicCallback(WebSocketRpcHandler.keep_alive, 30000).start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
    