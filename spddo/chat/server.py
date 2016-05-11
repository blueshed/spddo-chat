import time
import logging
import tornado.ioloop
import tornado.web
from tornado.options import define, options

from blueshed.micro.queue.pika_topic import PikaTopic
from blueshed.micro.utils.utils import gen_token
from blueshed.micro.utils.config import load_config
from spddo.chat.chat_handler import ChatHandler
from spddo.chat.main_handler import MainHandler

define("PORT", 8080, int, help="port to listen on")
define("CLOUDAMQP_URL", default='', help="broadcast queue")


def main():
    load_config()

    handlers = [
        (r"/websocket", ChatHandler),
        (r"/", MainHandler)
    ]
    settings = {
        "debug": True,
        "chat_clients": [],
        "server_id": gen_token(8)
    }

    if options.CLOUDAMQP_URL:
        def broadcast(body):
            for client in settings.get('chat_clients'):
                client.write_message(body)
        queue = PikaTopic(options.CLOUDAMQP_URL,
                          broadcast, 'chat-messages')
        settings['broadcast_queue'] = queue
        logging.info("broadcast_queue %s", options.CLOUDAMQP_URL)
        queue.connect()

    def keep_alive():
        msg = str(time.time()).encode("utf8")
        for client in settings["chat_clients"]:
            client.ping(msg)
    tornado.ioloop.PeriodicCallback(keep_alive, 30000).start()

    application = tornado.web.Application(handlers, **settings)
    application.listen(options.PORT)
    logging.info("listening on port %s", options.PORT)

    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
