from pkg_resources import resource_filename  # @UnresolvedImport

import logging
import os
from tornado.web import authenticated, RequestHandler, asynchronous
from tornado.concurrent import Future
from blueshed.micro.handlers.user_mixin import UserMixin
from blueshed.micro.utils.json_utils import dumps
from spddo.mongo.s3 import put_s3
from urllib.parse import urlparse


class S3PutHandler(UserMixin, RequestHandler):

    def initialize(self, s3_config, bucket, cors_origin=None):
        self.s3_config = s3_config
        self.bucket = bucket
        self.cors_origin = cors_origin

    def get_template_path(self):
        return resource_filename('spddo.mongo', "s3")

    def check_origin(self):
        url = self.request.headers.get("Referer")
        if url:
            o = urlparse(url)
            origin = "{}://{}".format(o.scheme, o.hostname)
            if o.port:
                origin = "{}:{}".format(origin, o.port)
            if origin in self.cors_origin:
                return origin

    def options(self, path=None):
        origin = self.check_origin()
        if origin in self.cors_origin:
            self.set_header("Access-Control-Allow-Origin", origin)
            self.set_header('Access-Control-Allow-Methods', 'GET,POST,OPTIONS')
            self.set_header('Access-Control-Allow-Headers',
                            'Origin, X-Requested-With, Content-Type, Accept, Key, Cache-Control')
            self.set_header('Access-Control-Max-Age', 3000)
            self.set_status(204)
            self.finish()
        else:
            RequestHandler.options(self)

    @authenticated
    def get(self, prefix=None):
        if self.cors_origin:
            origin = self.check_origin()
            if origin in self.cors_origin:
                self.set_header("Access-Control-Allow-Origin", origin)
            else:
                RequestHandler.get(self)
                return
        self.render("s3_upload.html")

    @authenticated
    @asynchronous
    def post(self, prefix=None):

        logging.info("prefix value %r", prefix)
        if prefix is None or prefix is '':
            prefix = self.get_argument("prefix", None)
            logging.info("prefix adjusted to %r", prefix)

        def done(future):
            try:
                _, result = future.result()
                result["tid"] = os.getpid()
                self.write_result_finish(result)
            except Exception as ex:
                self.write_result_finish({"error": str(ex)})

        context = self.micro_context(
            self.current_user, -1, 'put_s3', {})

        result = put_s3.main(context,
                             s3path=prefix,
                             files=self.request.files,
                             aws_config=self.s3_config,
                             bucket_name=self.bucket)
        if isinstance(result, Future):
            result.add_done_callback(done)
        else:
            context, result = result
            self.write_result_finish(result)

    def write_result_finish(self, result):
        if self.cors_origin:
            origin = self.check_origin()
            if origin in self.cors_origin:
                self.set_header("Access-Control-Allow-Origin", origin)
            else:
                RequestHandler.post(self)
                self.finish()
                return
        self.set_header("Content-Type",
                        "application/json; charset=UTF-8")
        self.finish(dumps(result))
