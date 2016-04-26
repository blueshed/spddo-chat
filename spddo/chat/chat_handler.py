import tornado.websocket
import time


class ChatHandler(tornado.websocket.WebSocketHandler):
    '''
        Simple chat websocket handler
    '''

    @property
    def chat_clients(self):
        ''' access utility for application settings '''
        return self.settings["chat_clients"]

    @property
    def broadcast_queue(self):
        ''' access utility for application settings '''
        return self.settings.get("broadcast_queue")

    def broadcast(self, msg):
        '''
            send msg from this client
        '''
        queue = self.broadcast_queue
        if queue:
            queue.post(msg)
        else:
            ''' send local '''
            for client in self.chat_clients:
                client.write_message(msg)

    def open(self):
        ''' called when websocket opens '''
        ''' set our user name '''
        self.user = "{}:{}".format(
            self.settings.get("server_id"), hex(id(self)))
        ''' add ourselves to the client list '''
        self.chat_clients.append(self)
        ''' tell the client their user name '''
        self.write_message(self.user)
        ''' tell everyone the client is online '''
        self.broadcast("opened {}".format(self.user))

    def on_message(self, message):
        ''' tell everyone our message '''
        if message == "ping":
            self.write_message("pong")
        else:
            self.broadcast(u"{} said: {}".format(self.user, message))

    def on_close(self):
        ''' remove ourselves from the client list '''
        if self in self.chat_clients:
            self.chat_clients.remove(self)
        ''' tell everyone we off '''
        self.broadcast("closed {}".format(self.user))
