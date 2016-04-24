import os
import logging
import tornado.ioloop
import tornado.web
from tornado.options import options, define, parse_command_line
from spddo.chat.chat_handler import ChatHandler
from spddo.chat.main_handler import MainHandler
from spddo.chat.pika_broadcaster import PikaBroadcaster
import random
import string

define("port", 8080, int, help="port to listen on")
define("multi", default='local', help="are we talking to queues")
define("db_url", default='sqlite:///chat.db', help="database url")
define("db_pool_recycle", 3600, int,
       help="how many seconds to recycle db connection")


def gen_token(length=32):
    return ''.join(random.choice(string.hexdigits) for _ in range(length))


# what is my address in heroku?
# you can see I have a handler called broadcast
# ready to receive the posts

def main():

    queue = None
    if options.multi == "rabbit":
        queue = PikaBroadcaster()
        queue.connect()

    handlers = [
        (r"/websocket", ChatHandler),
        (r"/", MainHandler)
    ]
    settings = {
        "debug": True,
        "chat_clients": [],
        "broadcast_queue": queue,
        "server_id": gen_token(8)
    }

    application = tornado.web.Application(handlers, **settings)

    if queue:
        queue.set_application(application)

    port = int(os.environ.get("PORT", options.port))
    application.listen(port)
    logging.info("listening on port {}".format(port))
    tornado.ioloop.PeriodicCallback(ChatHandler.keep_alive, 30000).start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    parse_command_line()
    main()
