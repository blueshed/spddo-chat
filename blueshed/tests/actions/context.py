from blueshed.micro.utils import db_connection
from blueshed.micro.utils.base_context import BaseContext


class Context(BaseContext):
    """ Extend BaseContext to include a db session """

    @property
    def session(self):
        return db_connection.session()
