from pkg_resources import resource_filename  # @UnresolvedImport
from tornado import web, gen
from tornado.escape import json_decode
from blueshed.micro.utils.json_utils import dumps
from blueshed.micro.handlers.context_mixin import ContextMixin
from blueshed.micro.handlers.user_mixin import UserMixin
import logging


class RpcHandler(ContextMixin, UserMixin, web.RequestHandler):
    '''
        Uses a pool to call procedures supporting

        get:
            returns the meta data about a service
            or all services

            suffix .js returns a client control
            javascript object for websocket support

            suffix <service name>.html returns
            an html form to run the service

        post:
            form-encoded or json-encoded input
            result is always json
    '''

    def initialize(self, html_template=None, js_template=None):
        web.RequestHandler.initialize(self)
        self._html_template = html_template
        self._js_template = js_template

    def get_template_path(self):
        ''' overrides the template path to use this module '''
        if self._html_template is None and self._js_template is None:
            return resource_filename('blueshed.micro.handlers', "templates")
        return web.RequestHandler.get_template_path(self)

    def get(self, path=None):
        services = self.get_service(path)
        if services is None:
            services = self.settings['services']
            if path is not None and path.endswith(".js"):
                self.set_header('content-type', 'text/javascript')
                self.render(self._js_template or "api-tmpl.js",
                            services=services.values())
                return
        elif path is not None and path.endswith(".html"):
            self.render(self._html_template or "service.html",
                        service=services,
                        error=None,
                        result=None)
            return
        self.set_header('content-type', 'application/json; charset=UTF-8')
        self.write(dumps(services, indent=4))

    @gen.coroutine
    def post(self, path):
        if self.request.headers['content-type'] == "application/json; charset=UTF-8":
            kwargs = json_decode(self.request.body)
        elif self.request.headers['content-type'] == "application/x-www-form-urlencoded":
            kwargs = dict([(k, self.get_argument(k))
                           for k in self.request.body_arguments.keys()])
        else:
            raise web.HTTPError(400, 'content type not supported {}'.format(
                self.request.headers['content-type']))
        service = self.get_service(path)
        context = self.settings['micro_context'](-1, -1, service.name)
        try:
            logging.info("%s(%r)", service.name, kwargs)
            context, result = yield service.perform_in_pool(
                self.settings['micro_pool'],
                context, **kwargs)
            self.flush_context(context)
            self.check_current_user(context)
            self.write_result(context, result)
        except Exception as ex:
            self.write_err(context, ex)
