import tornado.web


class ApiPageHandler(tornado.web.RequestHandler):

    def get(self):
        self.render("api.html")
