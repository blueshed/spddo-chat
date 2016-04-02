import tornado.web



class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("websocketrpc.html", 
                    services=self.application.settings['services'].values())
