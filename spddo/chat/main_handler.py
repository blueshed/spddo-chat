'''
Created on 23 Sep 2015

@author: peterb
'''
import tornado.web

'''
    Simple template renderer
'''
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")