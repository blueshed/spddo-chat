from tornado import web, gen
from tornado.escape import json_decode
from blueshed.micro.utils.json_utils import dumps
from blueshed.micro.handlers.context_mixin import ContextMixin
from blueshed.micro.handlers.user_mixin import UserMixin


class RpcHandler(ContextMixin, UserMixin, web.RequestHandler):
    '''
        Uses a pool to call procedures supporting

        get:
            returns the meta data about a service
            or all services

        post:
            form-encoded or json-encoded input
            result is always json
    '''

    def get(self, path=None):
        services = self.get_service(path)
        if services is None:
            services = self.settings['services']
        self.set_header('content-type', 'application/json; charset=UTF-8')
        self.write(dumps(services, indent=4))

    @gen.coroutine
    def post(self, path):
        if self.request.headers['content-type'] == "application/json; charset=UTF-8":
            kwargs = json_decode(self.request.body)
        elif self.request.headers['content-type'] == "application/x-www-form-urlencoded":
            kwargs = dict(self.request.body_arguments)
        else:
            raise web.HTTPError(400, 'content type not supported {}'.format(
                self.request.headers['content-type']))
        service = self.get_service(path)
        try:
            context, result = yield service.perform_in_pool(
                self.settings['pool'],
                self.settings['context'](-1, -1, service.name), **kwargs)
            self.set_header('content-type', 'application/json; charset=UTF-8')
            self.check_current_user(context)
            self.write(dumps({
                'result': result
            }))
        except Exception as ex:
            self.write({
                "error": str(ex)
            })