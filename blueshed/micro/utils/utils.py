import datetime
import random
import string


def parse_date(value):
    """
        Returns a Python datetime.datetime object,
        the input must be in some date ISO format
    """
    result = None
    if value:
        try:
            result = datetime.datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%fZ")
        except:
            try:
                result = datetime.datetime.strptime(
                    value, "%Y-%m-%d %H:%M:%S.%f")
            except:
                try:
                    result = datetime.datetime.strptime(
                        value, "%Y-%m-%d %H:%M:%S")
                except:
                    result = datetime.datetime.strptime(value, "%Y-%m-%d")

    return result


def parse_unix_time(value):
    return datetime.datetime.fromtimestamp(int(value))


def patch_tornado():
    # to provide svg and gzip svg support
    import mimetypes
    import tornado.web

    mimetypes.add_type('image/svg+xml', '.svg')  # because its not there!
    tornado.web.GZipContentEncoding.CONTENT_TYPES.add('image/svg+xml')
    # because its not there!
    mimetypes.add_type('application/font-woff', '.woff')
    # because its not there!
    mimetypes.add_type('application/font-woff2', '.woff2')


def gen_token(length=32):
    return ''.join(random.choice(string.hexdigits) for _ in range(length))
