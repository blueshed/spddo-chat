from collections import OrderedDict
import inspect
import logging

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

    def perform(self, context, **kwargs):
        if self.has_context:
            kwargs[self.has_context] = context
        return self.f(**kwargs)

    def __str__(self):
        return "%s %s - %s" % (self.name, self.desc, self.docs)

    @classmethod
    def describe(cls, target):
        result = OrderedDict()
        for key in filter(lambda x: x[0] != '_', dir(target)):
            f = getattr(target, key)
            if inspect.isfunction(f):
                s = cls(key, f)
                LOGGER.info(s)
                result[key] = s
        return result

    def to_json(self):
        return {
            "name": self.name,
            "params": [str(p) for p in self.desc.parameters.values()],
            "docs": self.docs
        }
