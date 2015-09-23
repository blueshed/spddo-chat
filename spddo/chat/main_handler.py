'''
Created on 23 Sep 2015

@author: peterb
'''
import tornado.web


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")