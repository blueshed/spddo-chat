from blueshed.micro.utils.service import no_pool
import bmemcached
import os
import logging

mc = None


def init_mc():
    global mc
    if os.environ.get('MEMCACHEDCLOUD_SERVERS'):
        mc = bmemcached.Client(
            os.environ.get('MEMCACHEDCLOUD_SERVERS').split(','),
            os.environ.get('MEMCACHEDCLOUD_USERNAME'),
            os.environ.get('MEMCACHEDCLOUD_PASSWORD'))
        logging.info("caching: %s", os.environ.get('MEMCACHEDCLOUD_SERVERS'))
    else:
        mc = None


@no_pool
def cache_set(key: str, value: str=""):
    ''' sets a value in cache named key '''
    global mc
    assert isinstance(key, str), "key is not a string: %r" % key
    mc.set(key, value)


@no_pool
def cache_get(key: str) -> str:
    ''' get the value from cache named key '''
    global mc
    assert isinstance(key, str), "key is not a string: %r" % key
    return mc.get(key)
