from os.path import join
import hashlib

from boto.s3.connection import S3Connection, Location
from boto.s3.key import Key
from boto.exception import S3ResponseError


class S3Storage(object):

    def __init__(self, s3_access_key, s3_secret_key, s3_bucket_name, document_url,
            s3_location=None):
        self.document_url = document_url
        self.document_hash = hashlib.sha1(self.document_url).hexdigest()
        self.conn = S3Connection(s3_access_key, s3_secret_key)
        self.paths = {}

        if s3_location is None:
            s3_location = Location.EU

        try:
            self.bucket = self.conn.get_bucket(s3_bucket_name)
        except S3ResponseError, e:
            if e.status != 404:
                raise

            self.bucket = self.conn.create_bucket(self.bucket, location=s3_location)

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
