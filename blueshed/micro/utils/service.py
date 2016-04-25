from collections import OrderedDict
import inspect
import logging
from tornado.concurrent import Future
from tornado.ioloop import IOLoop
import os

LOGGER = logging.getLogger(__name__)


class Service(object):
    '''
       Wraps a function with a description so that it can be
       called synchronously or asynchronously
    '''

    def __init__(self, key, f):
        self.name = key
        self.desc = inspect.signature(f)
        self.docs = inspect.getdoc(f)
        self.f = f
        self.has_context = None
        for k, v in self.desc.parameters.items():
            if v.annotation == 'micro-context':
                self.has_context = k
                break

    def __str__(self):
        return "%s %s - %s" % (self.name, self.desc, self.docs)

    @classmethod
    def describe(cls, target):
        '''
            Will list target and inspect each
            function and return an instance of
            this class for each
        '''
        result = OrderedDict()
        for key in filter(lambda x: x[0] != '_', dir(target)):
            f = getattr(target, key)
            if inspect.isfunction(f):
                s = cls(key, f)
                LOGGER.info(s)
                result[key] = s
        return result

    def perform(self, context, **kwargs):
        '''
            Call synchronously
        '''
        if self.has_context:
            kwargs[self.has_context] = context
        return self.f(**kwargs)

    def perform_in_pool(self, pool, context, **kwargs):
        '''
            Call with a process pool executor
        '''
        logging.info("run %s %s", os.getpid(), context)
        logging.info(IOLoop.current(False))
        return pool.submit(self.run_in_pool,
                           self.f,
                           self.has_context,
                           context,
                           **kwargs)

    @classmethod
    def run_in_pool(cls, f, has_context, context, **kwargs):
        # globals from the parent process in the
        # IOLoop so clear them.
        if IOLoop.current(False):
            LOGGER.debug("clearing tornado globals")
            IOLoop.clear_current()
            IOLoop.clear_instance()
        LOGGER.debug("running %s %s", os.getpid(), context)
        if has_context:
            kwargs[has_context] = context
        result = f(**kwargs)
        if isinstance(result, Future):
            LOGGER.debug('running up tornado to complete')

            def done(*args, **kwargs):
                LOGGER.debug('stopping tornado')
                IOLoop.current().stop()
            result.add_done_callback(done)
            IOLoop.current().start()
            result = result.result()
        return context, result

    def to_json(self):
        return {
            "name": self.name,
            "params": [str(p) for p in self.desc.parameters.values()],
            "docs": self.docs
        }
