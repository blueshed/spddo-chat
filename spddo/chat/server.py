import os
import time
import dotenv
import logging
import tornado.ioloop
import tornado.web
from tornado.options import options, define, parse_command_line
from blueshed.micro.queue.pika_topic import PikaTopic
from blueshed.micro.utils.utils import gen_token
from spddo.chat.chat_handler import ChatHandler
from spddo.chat.main_handler import MainHandler

define("port", 8080, int, help="port to listen on")
define("multi", default='local', help="are we talking to queues")
define("db_url", default='sqlite:///chat.db', help="database url")
define("db_pool_recycle", 3600, int,
       help="how many seconds to recycle db connection")


# what is my address in heroku?
# you can see I have a handler called broadcast
# ready to receive the posts

def main():

    handlers = [
        (r"/websocket", ChatHandler),
        (r"/", MainHandler)
    ]
    settings = {
        "debug": True,
        "chat_clients": [],
        "server_id": gen_token(8)
    }
    application = tornado.web.Application(handlers, **settings)

    amqp_url = os.environ.get("CLOUDAMQP_URL", '')
    if amqp_url:
        def broadcast(body):
            for client in application.settings.get('chat_clients'):
                client.write_message(body)
        queue = PikaTopic(os.environ.get("CLOUDAMQP_URL"),
                          broadcast, 'chat-messages')
        application.settings['broadcast_queue'] = queue
        logging.info("broadcast_queue {}".format(amqp_url))
        queue.connect()

    port = int(os.environ.get("PORT", options.port))
    application.listen(port)
    logging.info("listening on port {}".format(port))

    def keep_alive():
        msg = str(time.time()).encode("utf8")
        for client in application.settings["chat_clients"]:
            client.ping(msg)
    tornado.ioloop.PeriodicCallback(keep_alive, 30000).start()
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    parse_command_line()
    if os.path.isfile('.env'):
        dotenv.load_dotenv('.env')
    main()
