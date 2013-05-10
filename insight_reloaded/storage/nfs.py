import logging
from os import path, chdir, listdir, makedirs
from os.path import join
from shutil import rmtree, copyfile, move
from tempfile import mkdtemp
import hashlib
try:
    from subprocess import STDOUT, check_output, CalledProcessError
except ImportError:  # check_output new in 2.7, so use a backport for <=2.6
    from subprocess32 import STDOUT, check_output, CalledProcessError


class NFSStorage(object):

    def __init__(self, destination_root, document_url, prefix_url):
        self.destination_root = destination_root
        self.document_url = document_url
        self.prefix_url = prefix_url

    def prepare(self):
        """Create a unique identifier for the document, create the path
        and return it.
        """
        doc_uuid = hashlib.sha1(self.document_url).hexdigest()
        document_path = join(self.destination_root, string_to_folder_path(doc_uuid))
        try:
            makedirs(document_path)
        except OSError:
            print "%s already exists." % document_path
        self.destination_folder = document_path
        return document_path

    def post_process(self, path, size):
        filename_end = path.split('_')[-1]  # <page_num>.png
        page_num = filename_end[:-4]  # remove the '.png' extension
        new_name = 'document_%s_p%s.png' % (size, page_num)
        self.save(path, new_name)

    def get_path(self, path):
        return join(self.destination_folder, path)

    def save(self, path, filename):
        move(path, join(self.destination_folder, filename))

    def get_url(self):
        return self.destination_folder.replace(self.destination_root,
            self.prefix_url)


def string_to_folder_path(s):
    """Split a string into 2-char length folders.

    >>> string_to_folder_path('3614816AA000002781')
    '361/481/6AA/000/002/781'

    """
    if s:
        size = len(s) / 3 * 3
        folders = [s[i:i + 3] for i in range(0, size, 3)]
        return path.join(*folders)
    return ""
