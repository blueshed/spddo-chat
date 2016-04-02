import tornado.web
import micro.func
from micro.utils.json_utils import dumps
import inspect as py_inspect
from collections import OrderedDict
from tornado.escape import json_decode, url_unescape
import logging
import os


def _fc_describe_service(instance):
    '''
        Returns a description of the public methods of this class
    '''
    methods = []
    for name in dir(instance):
        if name[0] == '_': continue
        method = getattr(instance,name)
        requires = []
        ignore_list = ['self','accl','context']
        if hasattr(method,'_access_permissions_'):
            requires = method._access_permissions_
            ignore_list.append("session")
        if hasattr(method,'__wrapped__'):
            method = method.__wrapped__
        if callable(method):
            spec = py_inspect.getfullargspec(method)
            args = [n for n in spec.args if n not in ignore_list]
            logging.debug('%s %s',name,py_inspect.formatargspec(spec.args))
            defaults = {}
            if spec.defaults:
                sdefaults = list(spec.defaults)
                sdefaults.reverse()
                for i,value in enumerate(sdefaults):
                    defaults[spec.args[-(i+1)]] = value if value is not None else '_optional_'
            docs = py_inspect.getdoc(method)
            description = OrderedDict([
                           ("name", name), 
                           ("args", args), 
                           ("defaults", defaults),
                           ("requires", requires), 
                           ("docs", docs)
                           ])
            methods.append(description)
    return methods

def signature(method):
    return ", ".join([arg for arg in method['args'] if arg not in ['context', 'session', 'user'] ])
    
def params(method):
    padding = ",\n\t\t"
    result = []
    for arg in method['args']:
        if arg not in ['context', 'session', 'user']:
            default = method["defaults"].get(arg)
            if default is not None and default != '_optional_':
                if default is "":
                    result.append("{0}: {0} || ''".format(arg))
                else:
                    result.append("{0}: {0} || {1!r}".format(arg,default))
            else:
                result.append("{0}: {0}".format(arg))
    return padding.join(result)

class ApiHandler(tornado.web.RequestHandler):
    
    @property
    def cookie_name(self):
        return self.application.settings.get('cookie_name')
    
    
    def get_current_user(self):
        result = self.get_secure_cookie(self.cookie_name)
        if result:
            result = json_decode(result.decode('utf-8'))
        return result

    def get(self, path=None):
        if path == ".json":
            self.write(dumps(self.application.settings["services"],indent=4))
        elif path ==".js":
            methods = _fc_describe_service(micro.func)
            self.render("api-tmpl.js",
                        methods=methods,
                        signature=signature,
                        params=params)
        elif path == ".html":
            self.render("api-tmpl.html")
        else:
            raise tornado.web.HTTPError(404, "unsupported format {}".format(path))
