from blueshed.micro.utils.base_context import BaseContext
from blueshed.micro.utils import mongo_connection


class AuthenticationException(Exception):
    pass


class Context(BaseContext):
    '''
        Extend Base context to include a Mongodb client
    '''

    @property
    def motor(self):
        return mongo_connection.client()

    def authenticated(self):
        if self.get_cookie('current_user') is None:
            raise AuthenticationException("not logged in")
