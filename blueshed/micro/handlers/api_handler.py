import tornado.web
from blueshed.micro.utils.json_utils import dumps
from pkg_resources import resource_filename  # @UnresolvedImport
from blueshed.micro.handlers.user_mixin import UserMixin
import logging
from tornado.web import asynchronous
from tornado.concurrent import Future
from tornado.ioloop import IOLoop
import functools


class ApiHandler(UserMixin, tornado.web.RequestHandler):
    '''
        Provides http access to services
    '''

    def __init__(self, application, request, **kwargs):
        UserMixin.__init__(self)
        tornado.web.RequestHandler.__init__(
            self, application, request, **kwargs)

    @property
    def services(self):
        return self.application.settings["services"]

    def get_template_path(self):
        ''' overrides the template path to use this module '''
        return resource_filename('blueshed.micro.handlers', "templates")

    def get(self, path=None):
        '''
            if path ends with .json then return a description of services

            else if path ends with .js then return a javascript client to the
            websocket rpc server

            else if the path is a service name return an html form to call
            it with
        '''
        if path == ".json":
            self.write(dumps(self.services, indent=4))
        elif path == ".js":
            self.set_header('content-type', "text/javascript")
            self.render("api-tmpl.js",
                        services=self.services.values())
        elif path and path[1:].split(".")[0] in self.services:
            service = path[1:].split(".")[0]
            if path.endswith(".html"):
                self.render("service.html",
                            service=self.services[service],
                            error=None,
                            result=None)
            else:
                raise tornado.web.HTTPError(
                    404, "unsupported format {}".format(path))
        else:
            raise tornado.web.HTTPError(
                404, "unsupported format {}".format(path))

    @asynchronous
    def post(self, path=None):
        '''
            handle the post from the html form provided by get
            or marshall the arguments to the service expressed
            by path
        '''
        if path and path[1:].split(".")[0] in self.services:
            service = self.services[path[1:].split(".")[0]]
            kwargs = {}
            for param in service.desc.parameters.values():
                if param.name in ['context']:
                    continue
                kwargs[param.name] = self.get_argument(param.name, None)
            context = self.micro_context(
                self.current_user, -1, service.name, {})
            try:
                result = service.perform(context, **kwargs)
                if isinstance(result, Future):
                    IOLoop.current().add_future(
                        result,
                        functools.partial(self.handle_async_result, path,
                                          context))
                else:
                    self.handle_result(path, context, result)
            except Exception as ex:
                logging.exception(ex)
                self.handle_result(path, context, None, str(ex))
        else:
            raise tornado.web.HTTPError(
                404, "unsupported format {}".format(path))

    def handle_async_result(self, path, context, future):
        ''' handles async services '''
        try:
            self.handle_result(path, context, future.result())
        except Exception as ex:
            logging.exception(ex)
            self.handle_result(path, context, None, str(ex))

    def handle_result(self, path, context, result, error=None):
        ''' formats the result or error and responds '''
        logging.info("%s - %s - %s - %s", path, context, result, error)
        if error is None:
            if context.cookies.get('current_user') != self.current_user:
                self.set_current_user(context.cookies.get('current_user'))
                next_ = self.get_argument('next', None)
                if next_:
                    self.redirect(next_)
        if path.endswith(".js"):
            if error:
                self.write({"error": error})
            else:
                self.write(result)
            self.finish()
        else:
            self.render("service.html", service=self.services[
                        path[1:]], error=error, result=result)
