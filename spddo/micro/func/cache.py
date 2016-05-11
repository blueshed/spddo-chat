from blueshed.micro.utils.service import no_pool
from tornado.options import define, options
import bmemcached
import logging

mc = None

define("MEMCACHEDCLOUD_SERVERS", "")
define("MEMCACHEDCLOUD_USERNAME", "")
define("MEMCACHEDCLOUD_PASSWORD", "")


def init_mc():
    global mc
    if options.MEMCACHEDCLOUD_SERVERS:
        mc = bmemcached.Client(
            [options.MEMCACHEDCLOUD_SERVERS],
            options.MEMCACHEDCLOUD_USERNAME,
            options.MEMCACHEDCLOUD_PASSWORD)
        logging.info("caching: %s", options.MEMCACHEDCLOUD_SERVERS)
    else:
        mc = None


@no_pool
def cache_set(key: str, value: str="") -> bool:
    ''' sets a value in cache named key '''
    global mc
    assert mc, "no memcache service configured"
    assert isinstance(key, str), "key is not a string: %r" % key
    mc.set(key, value)
    return True


@no_pool
def cache_get(key: str) -> str:
    ''' get the value from cache named key '''
    global mc
    assert mc, "no memcache service configured"
    assert isinstance(key, str), "key is not a string: %r" % key
    return mc.get(key)
