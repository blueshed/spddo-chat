from tornado.log import enable_pretty_logging
from tornado.ioloop import IOLoop
from tornado.concurrent import Future
import multiprocessing
import functools
import logging
import os
from functools import wraps
import importlib

LOGGER = logging.getLogger(__name__)

static_pool = None

def pool(f):
    @wraps(f)
    def call(context=None, *args, **kwargs):
        global static_pool
        if static_pool is not None:
            if context:
                kwargs["context"]=context
            LOGGER.info('sending to pool')
            return static_pool.apply_future(f, *args, **kwargs)
        else:
            try:
                if context:
                    kwargs["context"]=context
                LOGGER.info('calling')
                result = f(*args, **kwargs)
                LOGGER.info('pool result %s',result)
                if isinstance(result, Future):
                    LOGGER.info('running up tornado to complete')
                    def done(*args, **kwargs):
                        IOLoop.current().stop()
                    IOLoop.current().add_future(result, done)
                    IOLoop.current().start()
                    result = result.result()
                if context:
                    LOGGER.info('returning context')
                    return context, result
                return result
            except Exception as ex:
                LOGGER.exception(ex)
                raise
    return call


def _async_runner_(_module_, _fname_, *args, **kwargs):
    module = importlib.import_module(_module_) 
    return getattr(module,_fname_)(*args, **kwargs)

class Pool():
    
    @classmethod
    def pool_init(*args):
        global static_pool
        enable_pretty_logging()
        LOGGER.info('pool init static_pool %r',static_pool)
        LOGGER.info("pool connected %s", os.getpid())
    
    def __init__(self, service_root, count, pool_init=None, *args):
        global static_pool
        self._service_root_ = service_root.__name__
        self._args_ = args
        self._pool_ = multiprocessing.Pool(count, # @UndefinedVariable
                                           initializer=pool_init if pool_init else Pool.pool_init, 
                                           initargs=self._args_)  
        static_pool = self

    def close(self):
        self._pool_.terminate()
        self._pool_.join()
        LOGGER.info("pool closed")
        
    def run_callback(self, future, result):
        LOGGER.info("pool callback")
        IOLoop.instance().add_callback(future.set_result, result)
        
    def run_errback(self, future, err):
        LOGGER.info("pool errback")
        IOLoop.instance().add_callback(future.set_exception, err)


    def apply_future(self, f, *args, **kwargs):
        future = Future()
        arguments = [self._service_root_, f.__name__]
        arguments.extend(args)
        self._pool_.apply_async(_async_runner_, arguments, kwds=kwargs,
                                callback=functools.partial(self.run_callback, future),
                                error_callback=functools.partial(self.run_errback, future))
        return future
