# -*- coding: utf-8 -*-
import httpretty
import unittest
import json
from mock import MagicMock, patch
import sys

from os.path import join, dirname

from insight_reloaded.worker import start_worker

TEST_FILE = join(dirname(__file__), 'test.pdf')


class InsightWorkerTest(unittest.TestCase):

    def test_start_worker(self):
        # Set a job in queue
        job = {"url": "http://my_file_url.com/file.pdf",
               "callback": "http://requestb.in/",
               "max_previews": 500,
               "hash": "4c3d8620ba07a52587dc4270ced35e255a8ae7de",
               "crop": 10}

        def redis_blpop_mock(*args, **kwargs):
            yield (None, json.dumps(job))
            yield sys.exit(0)

        generator = redis_blpop_mock()

        # Mock the redis blpop job
        redis_client = MagicMock()
        redis_client.blpop = lambda *args: next(generator)
        httpretty.register_uri(httpretty.GET,
                               "http://my_file_url.com/file.pdf",
                               content_type='application/pdf',
                               body=open(TEST_FILE).read())
        httpretty.register_uri(httpretty.POST, "http://requestb.in/",
                               body="ok")

        # start_worker and patch settings
        httpretty.enable()
        with patch('insight_reloaded.worker.redis', redis_client), \
                patch('insight_reloaded.worker.STORAGE_CLASS',
                      'insight_reloaded.storage.file_system:'
                      'FileSystemStorage'):
            try:
                start_worker(['insight_worker'])
            except SystemExit:
                pass
        httpretty.disable()

        # Verify callback
        callback_data = httpretty.last_request().parsed_body
        self.assertIn('docviewer_url', callback_data)
        self.assertIn('num_pages', callback_data)
        self.assertIn('success', callback_data)
