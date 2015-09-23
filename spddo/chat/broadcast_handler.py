'''
Created on 23 Sep 2015

@author: peterb
'''
import tornado.web


'''
    Broadcast handler is called by IronMQ push subscription
'''
class BroadcastHandler(tornado.web.RequestHandler):
    
    @property
    def chat_clients(self):
        ''' access utility for application settings '''
        return self.application.settings["chat_clients"]
    
    
    def post(self):
        ''' called when a post in received'''
        
        msg = self.request.body
        for client in self.chat_clients:
            client.write_message(msg)