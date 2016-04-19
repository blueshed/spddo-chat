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

    def __init__(self, application, request, **kwargs):
        UserMixin.__init__(self)
        tornado.web.RequestHandler.__init__(
            self, application, request, **kwargs)

    @property
    def services(self):
        return self.application.settings["services"]

    def get_template_path(self):
        return resource_filename('blueshed.micro', "handlers")

    def get(self, path=None):
        if path == ".json":
            self.write(dumps(self.services, indent=4))
        elif path == ".js":
            self.set_header('content-type', "text/javascript")
            self.render("api-tmpl.js",
                        services=self.services.values())
        elif path and path[1:] in self.services:
            self.render("service.html",
                        service=self.services[path[1:]],
                        error=None,
                        result=None)
        else:
            raise tornado.web.HTTPError(
                404, "unsupported format {}".format(path))

    @asynchronous
    def post(self, path=None):
        if path and path[1:] in self.services:
            service = self.services[path[1:]]
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
        try:
            self.handle_result(path, context, future.result())
        except Exception as ex:
            logging.exception(ex)
            self.handle_result(path, context, None, str(ex))

    def handle_result(self, path, context, result, error=None):
        logging.info("%s - %s - %s - %s", path, context, result, error)
        if error is None:
            if context.cookies.get('current_user') != self.current_user:
                self.set_current_user(context.cookies.get('current_user'))
                next_ = self.get_argument('next', None)
                if next_:
                    self.redirect(next_)
        self.render("service.html", service=self.services[
                    path[1:]], error=error, result=result)
