import tornado.web

class MainHandler(tornado.web.RequestHandler):
    '''
        Simple template renderer
    '''

    def get(self):
        self.render("index.html")