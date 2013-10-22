import os
import os.path
import shutil
import unittest

from tempfile import mkstemp, mkdtemp

from insight_reloaded.storage.file_system import FileSystemStorage


class FileSystemStorageTestCase(unittest.TestCase):

    def setUp(self):
        _, self.source_file = mkstemp()
        self.source_url = 'http://localhost:9200/an/random/url'
        self.destination_root = mkdtemp()
        self.prefix_url = 'http://localhost/prefix'
        self.content = 'Source file !'

        with open(self.source_file, 'wb') as f:
            f.write(self.content)

        self.storage = FileSystemStorage(self.source_url,
                                         self.destination_root,
                                         self.prefix_url)

    def tearDown(self):
        try:
            os.remove(self.source_file)
            shutil.rmtree(self.destination_root)
        except os.error:
            pass

#     def test_prepare_and_save(self):
#         filename = 'document_p1.png'
#         self.storage.prepare()
#         self.storage.save(self.source_file, filename)
# 
#         file_path = self.storage.get_path(filename)
# 
#         self.assertTrue(os.path.exists(file_path))
# 
#         with open(file_path) as f:
#             self.assertEqual(f.read().strip(), self.content)
