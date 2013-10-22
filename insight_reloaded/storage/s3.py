from os.path import join

from boto.s3.connection import S3Connection, Location
from boto.s3.key import Key
from boto.exception import S3ResponseError
from insight_reloaded.insight_settings import (
    S3_ACCESS_KEY, S3_SECRET_KEY, S3_BUCKET_NAME
)


class S3Storage(object):

    def __init__(self, document_url, document_hash, s3_location=None):
        self.document_url = document_url

        self.document_hash = document_hash

        self.conn = S3Connection(S3_ACCESS_KEY, S3_SECRET_KEY)
        self.paths = {}

        if s3_location is None:
            s3_location = Location.EU

        try:
            self.bucket = self.conn.get_bucket(S3_BUCKET_NAME)
        except S3ResponseError, e:
            if e.status != 404:
                raise

            self.bucket = self.conn.create_bucket(self.bucket,
                                                  location=s3_location)

    def prepare(self):
        """Do nothing
        """
        pass

    def get_path(self, filename):
        return self.paths[filename]

    def save(self, path, filename):
        self.paths[filename] = path
        key = Key(self.bucket)
        key.storage_class = 'REDUCED_REDUNDANCY'
        key.key = join(self.document_hash, filename)
        key.set_contents_from_filename(path)

    def get_base_document_url(self):
        return self.document_hash
