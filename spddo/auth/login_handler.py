import tornado.web
from spddo.auth.actions.login import login
from spddo.auth.actions.context import Context
import logging


class LoginHandler(tornado.web.RequestHandler):

    def get(self, path=None, email=None, error=None):
        self.render("login.html",
                    email=email,
                    next=self.get_argument("next", "/"),
                    error=error)

    def post(self, path=None):
        context = Context(-1, -1, "login")

        try:
            email = self.get_argument("email")
            password = self.get_argument("password")
            result = login(context, email, password)
        except Exception as ex:
            logging.exception(ex)
            self.get(email=self.get_argument("email", None),
                     error=str(ex))
            return

        self.render("loggedin.html", **result)
