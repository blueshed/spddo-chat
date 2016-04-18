import tornado.web


class LogoutHandler(tornado.web.RequestHandler):
    
    @property
    def cookie_name(self):
        return self.application.settings.get('cookie_name')
    
    def get(self):
        self.clear_cookie(self.cookie_name)
        self.redirect(self.get_argument("next", "/"))