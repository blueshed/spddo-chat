import tornado.web
from blueshed.micro.utils.json_utils import dumps
from tornado.escape import json_decode
from pkg_resources import resource_filename  # @UnresolvedImport


class ApiHandler(tornado.web.RequestHandler):
    
    @property
    def cookie_name(self):
        return self.application.settings.get('cookie_name')
    
    def get_template_path(self):
        return resource_filename('blueshed.micro',"handlers")
        
    def get_current_user(self):
        result = self.get_secure_cookie(self.cookie_name)
        if result:
            result = json_decode(result.decode('utf-8'))
        return result

    def get(self, path=None):
        if path == ".json":
            self.write(dumps(self.application.settings["services"],indent=4))
        elif path ==".js":
            self.render("api-tmpl.js",
                        services=self.application.settings['services'].values())
        else:
            raise tornado.web.HTTPError(404, "unsupported format {}".format(path))
