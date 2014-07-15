from os.path import join

import pyrax
pyrax.set_setting("identity_type", "rackspace")

from insight_reloaded.insight_settings import (
    CLOUDFILES_USERNAME, CLOUDFILES_API_KEY, CLOUDFILES_COUNTAINER,
    CLOUDFILES_SERVICENET, CLOUDFILES_DEFAULT_REGION
)
from insight_reloaded.preview import PreviewException


class CloudFilesStorage(object):

    def __init__(self, document_url, document_hash, cloudfiles_location=None):
        self.document_url = document_url
        self.document_hash = document_hash

        if cloudfiles_location is None:
            cloudfiles_location = CLOUDFILES_DEFAULT_REGION

        pyrax.set_default_region(cloudfiles_location)
        pyrax.set_credentials(CLOUDFILES_USERNAME, CLOUDFILES_API_KEY,
                              region=cloudfiles_location)
        self.paths = {}

        self.client = pyrax.connect_to_cloudfiles(
            cloudfiles_location, public=not CLOUDFILES_SERVICENET)
        if self.client is None:
            err_msg = ('Error during connection to cloudfiles, region {0} is'
                       ' likely to be wrong.'.format(cloudfiles_location))
            raise PreviewException(err_msg)
        self.container = self.client.create_container(CLOUDFILES_COUNTAINER)

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
