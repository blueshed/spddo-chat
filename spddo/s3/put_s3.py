from PIL import Image
import logging
import os
import io
from .bucket import Bucket

TYPE_MAP = {
    ".jpg": ("JPEG", 'image/jpeg'),
    ".jpeg": ("JPEG", 'image/jpeg'),
    ".png": ("PNG", 'image/png'),
    ".gif": ("GIF", 'image/gif')
}

THUMB_SIZE = (184, 138)
SMALL_SIZE = (368, 276)


def _make_one(bucket, data, size, fType, fMime, prefix, fActual, fExt):
    img = Image.open(io.BytesIO(data))
    img.thumbnail(size)
    img_io = io.BytesIO()
    img.save(img_io, fType)
    img_io.seek(0)
    key_path = "{}/{}{}".format(prefix, fActual,
                                fExt) if prefix else "{}{}".format(fActual,
                                                                   fExt)
    key = bucket.add(img_io.read(), key=key_path, meta={'content-type': fMime})
    return bucket.gen_abs_url(key)


def main(s3path, files, aws_config, bucket_name):
    bucket = Bucket.get_bucket_by_name(aws_config, bucket_name)
    result = {}
    for key in files:
        for fileinfo in files[key]:
            fname = fileinfo['filename']
            _, fExt = os.path.splitext(fname)
            fType, fMime = TYPE_MAP.get(fExt.lower(), (None, None))
            if fType is None:
                raise Exception("File Type not accepted: {}".format(fType))
            key_path = "{}/original{}".format(
                s3path, fExt) if s3path else "original{}".format(fExt)
            s3key = bucket.add(fileinfo['body'], key=key_path, meta={
                               "original_name": fname,
                               "content-type": fMime})
            result[key] = {
                "name": fname,
                "key": s3key,
                "original": bucket.gen_abs_url(s3key)
            }
            result[key]["small"] = _make_one(bucket,
                                             fileinfo['body'],
                                             THUMB_SIZE,
                                             fType, fMime,
                                             s3path,
                                             "small",
                                             fExt)
            result[key]["thumb"] = _make_one(bucket,
                                             fileinfo['body'],
                                             THUMB_SIZE,
                                             fType, fMime,
                                             s3path,
                                             "thumbnail",
                                             fExt)
    return result
