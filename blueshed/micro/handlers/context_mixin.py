from tornado import web
from blueshed.micro.utils.json_utils import dumps
import logging
from tornado.escape import json_encode
from tornado.httpclient import HTTPError


class ContextMixin(object):

    context_clients = []

    @property
    def micro_context(self):
        ''' return the context class declared in application settings'''
        return self.settings.get('micro_context')

    def get_service(self, path):
        if path.startswith("/"):
            path = path[1:]
        if '.' in path:
            path = path.split(".")[0]
        if path:
            service = self.settings['services'].get(path)
            if service is None:
                raise web.HTTPError(400, "no service named {}".format(path))
            return service

    def flush_context(self, context):
        ''' after a success broadcast anything in the context '''
        queue = self.application.settings.get("broadcast_queue")
        for signal, message in context.broadcasts:
            data = dumps({
                "signal": signal,
                "message": message
            })
            if queue:
                queue.post(data)
            else:
                for client in self.context_clients:
                    client.write_message(data)
        context.flushed()

    def check_current_user(self, context):
        if context.cookies.get('current_user') != self.current_user:
            self.set_current_user(context.cookies.get('current_user'))

    def update_result_data(self, context, data):
        if context.cookies.get('current_user') != self.current_user:
            setattr(self, '_current_user', context.cookies.get('current_user'))
            data['cookie_name'] = self.cookie_name
            data['cookie'] = web.create_signed_value(
                self.settings["cookie_secret"],
                self.cookie_name,
                dumps(self.current_user)).decode("utf-8")

    def write_result(self, context, result):
        """Format a result response."""
        data = {
            'id': context.action_id,
            'action': context.action,
            'result': result,
            'status_code': 200,
            'error': None,
            'message': None,
        }
        self.update_result_data(context, data)

        content = json_encode(data)

        if hasattr(self, "write_message"):
            self.write_message(content)
        else:
            self.set_header('content-type', 'application/json; charset=UTF-8')
            self.write(content)

    def write_err(self, context, ex):
        """Format an error response."""
        logging.exception(str(ex))
        is_http = isinstance(ex, HTTPError)
        error = str(ex) if is_http else '500 Internal Server Error'
        code = ex.status_code if is_http else 500
        if is_http:
            message = ex.reason
        elif self.settings.get('allow_exception_messages'):
            message = str(ex)
        else:
            message = "Cripes, an unexpected error!"

        err = json_encode({
            'id': context.action_id,
            'action': context.action,
            'result': None,
            'status_code': code,
            'error': error,
            'message': message,
        })

        if hasattr(self, "write_message"):
            self.write_message(err)
        else:
            self.set_header('content-type', 'application/json; charset=UTF-8')
            self.write(err)
