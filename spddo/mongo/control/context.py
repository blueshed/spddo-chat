from blueshed.micro.utils.base_context import BaseContext
from blueshed.micro.utils import mongo_connection


class Context(BaseContext):
    '''
        Extend Base context to include a Mongodb client
    '''
            
    @property
    def motor(self):
        return mongo_connection.client()
