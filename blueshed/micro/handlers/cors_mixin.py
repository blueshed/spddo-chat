from urllib.parse import urlparse
from tornado.web import HTTPError


class CorsMixin(object):
    '''
        This assumes that you're subclassing a websocket / request handler
        Your 'cors_origins' should be a url string list placed in settings.
    '''

    _cors_methods_ = 'GET,POST,PUT,DELETE,OPTIONS'

    def set_cors_methods(self, method_string):
        self._cors_methods_ = method_string

    @property
    def origin_whitelist(self):
        return self.settings.get('cors_origins')

    @property
    def request_origin(self):
        url = self.request.headers.get("Referer")
        if url:
            o = urlparse(url)
            origin = o.scheme + "://" + o.hostname
            if o.port:
                origin = "{}:{}".format(origin, o.port)
            return origin

    def set_default_headers(self):
        if self.request_origin in self.origin_whitelist:
            self.set_header("Access-Control-Allow-Origin", self.request_origin)
            self.set_header('Access-Control-Allow-Credentials', 'true')

    def cors_options(self, *arg, **kwargs):
        if self.request_origin in self.origin_whitelist:
            self.set_header("Access-Control-Allow-Origin", self.request_origin)
            self.set_header('Access-Control-Allow-Credentials', 'true')
            self.set_header('Access-Control-Allow-Methods', self._cors_methods_)
            self.set_header('Access-Control-Allow-Headers',
                            'Origin, X-Requested-With, Content-Type, Accept, Key, Cache-Control')
            self.set_header('Access-Control-Max-Age', 3000)
            self.set_status(204)
            self.finish()
        else:
            raise HTTPError(403)