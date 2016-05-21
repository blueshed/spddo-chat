from blueshed.micro.orm import db_connection
from blueshed.micro.utils.base_context import BaseContext
from spddo.todo import model


class Context(BaseContext):
    """ Extend BaseContext to include a db session """

    def __init__(self, client_id, action_id, action, cookies=None,
                 handler=None):
        BaseContext.__init__(self, client_id, action_id, action,
                             cookies=cookies, handler=handler)
        if handler and handler.request.files:
            self.files = handler.request.files

    @property
    def session(self):
        return db_connection.session()

    def broadcast(self, signal, message, accl=None):
        BaseContext.broadcast(self, signal, message, accl=accl)
        return message

    def get_user(self, session):
        if self.cookies.get("current_user"):
            return session.query(model.User).get(
                self.cookies["current_user"]["id"])
