from tornado.escape import json_decode
from blueshed.micro.utils.json_utils import dumps


class UserMixin(object):

    @property
    def micro_context(self):
        return self.application.settings.get('micro_context')

    @property
    def cookie_name(self):
        return self.application.settings.get('cookie_name')

    def get_current_user(self):
        result = self.get_secure_cookie(self.cookie_name)
        if result:
            result = json_decode(result.decode('utf-8'))
        return result

    def set_current_user(self, value):
        self.set_secure_cookie(self.cookie_name, dumps(value))
