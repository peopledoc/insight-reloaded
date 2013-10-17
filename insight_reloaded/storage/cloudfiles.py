from os.path import join
import hashlib

import pyrax
pyrax.set_setting("identity_type", "rackspace")

from insight_reloaded.insight_settings import (CLOUDFILES_USERNAME,
    CLOUDFILES_API_KEY, CLOUDFILES_COUNTAINER)


class CloudFilesStorage(object):

    def __init__(self, document_url, document_hash, cloudfiles_location=None):
        self.document_url = document_url
        self.document_hash = document_hash

        if cloudfiles_location is None:
            cloudfiles_location = "LON"

        pyrax.set_default_region(cloudfiles_location)
        pyrax.set_credentials(CLOUDFILES_USERNAME, CLOUDFILES_API_KEY)
        self.paths = {}

        self.container = pyrax.cloudfiles.create_container(CLOUDFILES_COUNTAINER)

    def prepare(self):
        """Do nothing
        """
        pass

    def get_path(self, filename):
        return self.paths[filename]

    def save(self, path, filename):
        self.paths[filename] = path
        self.container.upload_file(path, join(self.document_hash, filename))

    def get_base_document_url(self):
        return self.document_hash
