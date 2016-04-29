from pkg_resources import resource_filename  # @UnresolvedImport

import logging
import os
from tornado.web import authenticated, RequestHandler, asynchronous
import tornado.concurrent
from blueshed.micro.web.context_mixin import ContextMixin
from blueshed.micro.web.cors_mixin import CorsMixin, cors
import functools


class S3PutHandler(ContextMixin, CorsMixin, RequestHandler):

    def initialize(self, s3_config, bucket, service, cors_origins=None):
        RequestHandler.initialize(self)
        self.s3_config = s3_config
        self.bucket = bucket
        self.service = service
        self.set_cors_methods('GET,POST,OPTIONS')
        self.set_cors_whitelist(cors_origins)

    def get_template_path(self):
        return resource_filename('spddo', "s3")

    def options(self):
        return self.cors_options()

    @cors
    def get(self, prefix=None):
        self.render("s3_upload.html")

    @asynchronous
    @cors
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
            self.current_user, -1, 'put_s3', {},
            self)
        try:
            kwargs = dict(s3path=prefix,
                          files=self.request.files,
                          aws_config=self.s3_config,
                          bucket_name=self.bucket)
            logging.info("%s(%r)", self.service.name, kwargs)
            result = self.service.perform(context, **kwargs)
            if tornado.concurrent.is_future(result):
                result.add_done_callback(
                    functools.partial(self.handle_future,
                                      self.service,
                                      context,
                                      True))
            else:
                self.handle_result(self.service, context, result)
                self.finish()
        except Exception as ex:
            self.write_err(context, ex)
            self.finish()
