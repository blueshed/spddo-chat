from pkg_resources import resource_filename  # @UnresolvedImport
from tornado.web import RequestHandler
import cairosvg
import json
import os


class ColoursHandler(RequestHandler):
    ''' returns a .png for an svg template '''

    def get_template_path(self):
        ''' overrides the template path to use this module '''
        return resource_filename('spddo.mongo', "svg")

    def get(self, path=None):
        colours = json.load(open(os.path.join(self.get_template_path(),
                                              "colours.json")))

        def colour_by_id(arg, default):
            id_ = int(self.get_argument(arg, default))
            for colour in colours.get("colours", []):
                if colour.get("id") == id_:
                    return colour['colour']
            raise Exception("No such colour {}".format(id_))

        svg = self.render_string(
            "colours.svg",
            colour_one=colour_by_id("one", "4"),
            colour_two=colour_by_id("two", "4"),
            colour_three=colour_by_id("three", "4"),
            colour_letter=colour_by_id("letter", "5"),
            initial=self.get_argument("initial", ""))

        width = int(self.get_argument("w", 64))
        height = int(self.get_argument("h", 64))

        self.set_header("content-type", "image/png")
        self.write(cairosvg.svg2png(svg,  # @UndefinedVariable
                                    parent_width=width,
                                    parent_height=height))
