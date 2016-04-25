from blueshed.micro.utils.pool import Pool
from blueshed.micro.utils.db_connection import db_init
import logging


LOGGER = logging.getLogger(__name__)


class SQLPool(Pool):

    @classmethod
    def sql_pool_init(cls, db_url, db_echo=False, db_pool_recycle=None):
        Pool.pool_init()
        db_init(db_url, db_echo, db_pool_recycle)

    def __init__(self, service_root, count,
                 db_url, db_echo=False, db_pool_recycle=None):
        super().__init__(service_root, count, SQLPool.sql_pool_init,
                         db_url, db_echo, db_pool_recycle)
