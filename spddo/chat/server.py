'''
Created on 23 Sep 2015

@author: peterb
'''

import os
import logging
import tornado.ioloop
import tornado.web
from tornado.options import options, define, parse_command_line
from iron_mq import IronMQ
from spddo.chat.broadcast_handler import BroadcastHandler
from spddo.chat.chat_handler import ChatHandler
from spddo.chat.main_handler import MainHandler

define("port", 8080, int, help="port to listen on")
define("multi", default='no', help="are we talking to queues")


# what is my address in heroku?
# you can see I have a handler called broadcast
# ready to receive the posts

def main():
    
    queue = None
    if options.multi == 'yes':
        address = "" 
        mq = IronMQ(project_id=os.environ.get("IRON_MQ_PROJECT_ID"),
                    token=os.environ.get("IRON_MQ_TOKEN"))
        queue = mq.queue("broadcast_queue")
        queue.add_subscribers(address, push_type="multicast")
    
    handlers = [
        (r"/broadcast", BroadcastHandler),    
        (r"/websocket", ChatHandler),                                  
        (r"/", MainHandler)
    ]
    settings = {
        "debug":True, 
        "chat_clients": [],
        "broadcast_queue": queue
    }
    
    application = tornado.web.Application(handlers,**settings)
    
    port = int(os.environ.get("PORT", options.port))
    application.listen(port)
    logging.info("listening on port {}".format(port))
    tornado.ioloop.IOLoop.current().start()
    

if __name__ == "__main__":
    parse_command_line()
    main()