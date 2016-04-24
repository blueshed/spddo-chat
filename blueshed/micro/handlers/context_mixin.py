from tornado import web
from blueshed.micro.utils.json_utils import dumps


class ContextMixin(object):

    context_clients = []

    @property
    def micro_context(self):
        ''' return the context class declared in application settings'''
        return self.settings.get('micro_context')

    def get_service(self, path):
        if path.startswith("/"):
            path = path[1:]
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
            self.set_current_user(context.cookies['current_user'])

    def update_result_data(self, context, data):
        if context.cookies.get('current_user') != self.current_user:
            setattr(self, '_current_user', context.cookies['current_user'])
            data['cookie_name'] = self.cookie_name
            data['cookie'] = web.create_signed_value(
                self.settings["cookie_secret"],
                self.cookie_name,
                dumps(self.current_user)).decode("utf-8")
