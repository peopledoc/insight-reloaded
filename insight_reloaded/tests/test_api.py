# -*- coding: utf-8 -*-
import json
import redis

from tornado.testing import AsyncHTTPTestCase

from insight_reloaded.api import application
from insight_reloaded import __version__ as VERSION

from insight_reloaded.insight_settings import (
    REDIS_HOST, REDIS_PORT, REDIS_DB, DEFAULT_REDIS_QUEUE_KEY
)


from tornado import ioloop


class InsightApiHTTPTest(AsyncHTTPTestCase):

    def get_new_ioloop(self):
        return ioloop.IOLoop.instance()

    def get_app(self):
        return application

    def tearDown(self):
        # 1. Empty the status queue
        r = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT,
                              db=REDIS_DB)
        while r.lpop(DEFAULT_REDIS_QUEUE_KEY):
            pass

        return super(InsightApiHTTPTest, self).tearDown()

    def test_api_version(self):
        self.http_client.fetch(self.get_url('/'), self.stop)
        response = self.wait()
        body_json = json.loads(response.body)
        self.assertIn('version', body_json)
        self.assertIn('insight_reloaded', body_json)

        self.assertEqual('insight-reloaded', body_json['name'])
        self.assertEqual(VERSION, body_json['version'])

    def test_api_request(self):
        self.http_client.fetch(self.get_url('/') +
                               u'?url=http://my_file_url.com/file.pdf',
                               self.stop)
        response = self.wait()
        json_body = json.loads(response.body)
        self.assertIn('insight_reloaded', json_body)
        self.assertEqual(json_body['number_in_queue'], 1)

    def test_api_url_missing(self):
        self.http_client.fetch(self.get_url('/') + '?arg=foobar', self.stop)
        response = self.wait()
        self.assertEqual(response.code, 404)

    def test_status(self):

        # 1. Check the status
        self.http_client.fetch(self.get_url('/status'), self.stop)
        response = self.wait()
        json_body = json.loads(response.body)
        self.assertDictEqual({"insight_reloaded": "There is 0 job in the "
                              "'insight-reloaded' queue.",
                              "number_in_queue": 0}, json_body)
        # 2. Add a job
        self.http_client.fetch(self.get_url('/') +
                               '?url=http://my_file_url.com/file.pdf',
                               self.stop)
        response = self.wait()
        self.assertEqual(response.code, 200)
        json_body = json.loads(response.body)
        self.assertDictEqual({"insight_reloaded": "Job added to queue "
                              "'insight-reloaded'.",
                              "number_in_queue": 1}, json_body)
