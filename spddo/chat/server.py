'''
Created on 23 Sep 2015

@author: peterb
'''

import tornado.ioloop
import tornado.web
from spddo.chat.chat_handler import ChatHandler
from spddo.chat.main_handler import MainHandler
import os
import logging


def main():
    application = tornado.web.Application([
            (r"/websocket", ChatHandler),                                  
            (r"/", MainHandler)
        ],
        debug=True, 
        chat_clients=[])
    
    port = int(os.environ.get("PORT", 8080))
    application.listen(port)
    logging.info("listening on port {}".format(port))
    tornado.ioloop.IOLoop.current().start()
    

if __name__ == "__main__":
    from tornado.options import parse_command_line

    parse_command_line()
    main()