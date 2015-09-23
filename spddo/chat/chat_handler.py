'''
Created on 23 Sep 2015

@author: peterb
'''
import tornado.websocket


class ChatHandler(tornado.websocket.WebSocketHandler):
    
    @property
    def chat_clients(self):
        return self.application.settings["chat_clients"]
    
    def broadcast(self, msg):
        for client in self.chat_clients:
            client.write_message(msg)
    
    def open(self):
        self.chat_clients.append(self)
        self.user = repr(self)
        self.write_message(self.user)
        self.broadcast("opened {}".format(self.user))

    def on_message(self, message):
        self.broadcast(u"{} said: {}".format(self.user,message))

    def on_close(self):
        if self in self.chat_clients:
            self.chat_clients.remove(self)
        self.broadcast("closed {}".format(self.user))