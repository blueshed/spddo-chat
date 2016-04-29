from blueshed.micro.utils.base_context import BaseContext
from blueshed.micro.orm import mongo_connection
from tornado.web import HTTPError


class Context(BaseContext):
    '''
        Extend Base context to include a Mongodb client
    '''

    @property
    def motor(self):
        return mongo_connection.client()

    def authenticated(self):
        if self.get_cookie('current_user') is None:
            raise HTTPError(403, "logged in required")
