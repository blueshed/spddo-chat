from pkg_resources import resource_filename  # @UnresolvedImport

import logging
import os
from tornado.web import authenticated, RequestHandler, asynchronous
from tornado.concurrent import Future
from tornado.ioloop import IOLoop
from blueshed.micro.handlers.user_mixin import UserMixin
from blueshed.micro.utils.json_utils import dumps
from spddo.mongo.s3 import put_s3


class S3PutHandler(UserMixin, RequestHandler):

    def initialize(self, s3_config, bucket):
        self.s3_config = s3_config
        self.bucket = bucket

    def get_template_path(self):
        return resource_filename('spddo.mongo', "s3")

    @authenticated
    def get(self, prefix=None):
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
            IOLoop.current().add_future(result, done)
        else:
            context, result = result
            self.write_result_finish(result)

    def write_result_finish(self, result):
        self.set_header("Content-Type",
                        "application/json; charset=UTF-8")
        self.finish(dumps(result))
