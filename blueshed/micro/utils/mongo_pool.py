from blueshed.micro.utils.pool import Pool
from blueshed.micro.utils.mongo_connection import db_init
import logging


LOGGER = logging.getLogger(__name__)


class MongoPool(Pool):

    @classmethod
    def mongo_pool_init(cls, db_url):
        Pool.pool_init()
        db_init(db_url)


    def __init__(self, service_root, count, db_url):
        super().__init__(service_root, count, MongoPool.mongo_pool_init, db_url)
