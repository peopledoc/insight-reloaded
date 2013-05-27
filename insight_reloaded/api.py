import json
import os

import tornadoredis
import tornado.web
import tornado.ioloop
import tornado.gen
import tornado.httpserver

from insight_reloaded.insight_settings import (
    REDIS_HOST, REDIS_PORT, REDIS_DB, SENTRY_DSN, REDIS_QUEUE_KEYS,
    DEFAULT_REDIS_QUEUE_KEY, CROP_SIZE)


try:
    from raven import Client
except ImportError:
    if SENTRY_DSN:
        SENTRY_DSN = None
        print "SENTRY_DSN is defined but raven isn't installed."


HERE = os.path.dirname(os.path.abspath(__file__))
try:
    with open(os.path.join(HERE, '../VERSION')) as f:
        VERSION = f.readlines()[0].strip()
except IOError:
    VERSION = 'N/A'

# Kombu connection
from kombu import Connection, Exchange, Queue
previews_exchange = Exchange('previews', 'direct', durable=True)

# Raw redis connection
c = tornadoredis.Client(host=REDIS_HOST, port=REDIS_PORT, selected_db=REDIS_DB)
c.connect()


class MainHandler(tornado.web.RequestHandler):
    """Convert the querystring in a REDIS job JSON."""

    @tornado.web.asynchronous
    def get(self, queue):
        print "GET!!!!!!!!!!!!!"
        # If there is no argument, display the version
        if self.request.arguments == {}:
            self.write(dict(insight_reloaded="Bonjour",
                            name="insight-reloaded",
                            version=VERSION))
            self.finish()
            return

        if not queue:
            queue = DEFAULT_REDIS_QUEUE_KEY

        if queue not in REDIS_QUEUE_KEYS:
            raise tornado.web.HTTPError(404, 'Queue "%s" not found' % queue)

        self.queue = queue

        # Else process the request
        params = {'url': self.get_argument("url", None),
                  'callback': self.get_argument("callback", None),
                  }
        # Get URL
        if params['url']:
            if params['url'].startswith('/'):
                params['url'] = '%s://%s%s' % (self.request.protocol,
                                               self.request.host,
                                               params['url'])
        else:
            raise tornado.web.HTTPError(404, 'Input file not found')

        # Max number of pages to compile
        try:
            params['max_previews'] = int(self.get_argument('pages', 20))
        except:
            params['max_previews'] = 20

        try:
            params['crop'] = int(self.get_argument('crop', 0))
        except ValueError:
            params['crop'] = CROP_SIZE

        message = params

        redis_address = 'redis://%s:%s/%s' % (REDIS_HOST, REDIS_PORT, REDIS_DB)

        previews_queue = Queue(self.queue, exchange=previews_exchange,
            routing_key=self.queue)

        print "PUSH!!!!!!!!!!!!! to queue %s" % self.queue

        with Connection(redis_address) as conn:
            with conn.Producer(serializer='json') as producer:
                producer.publish(message, exchange=previews_exchange,
                    routing_key=self.queue, declare=[previews_queue])

        self.write(dict(insight_reloaded="Job added to queue '%s'." %
                        self.queue))
        self.finish()
        # c.rpush(self.queue, message, callback=self.on_response)

    # def on_response(self, response):
    #     self.write(dict(insight_reloaded="Job added to queue '%s'." %
    #                     self.queue,
    #                     number_in_queue=response))
    #     self.finish()


class StatusHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, queue):
        if not queue:
            queue = DEFAULT_REDIS_QUEUE_KEY

        if queue not in REDIS_QUEUE_KEYS:
            raise tornado.web.HTTPError(404, "Queue '%s' not found" % queue)
        self.queue = queue
        c.llen(self.queue, callback=self.on_response)

    def on_response(self, response):
        self.write(dict(insight_reloaded="There is %d job in the '%s' queue." %
                        (response, self.queue),
                        number_in_queue=response))
        self.finish()


application = tornado.web.Application([
    (r"/([A-Za-z0-9_-]*)/?status", StatusHandler),
    (r"/([A-Za-z0-9_-]*)", MainHandler),
])


def main():
    if SENTRY_DSN:
        client = Client(dsn=SENTRY_DSN)
    else:
        client = None
    print "Launch tornado ioloop"
    application.listen(8888)
    try:
        tornado.ioloop.IOLoop.instance().start()
    except Exception:
        if client:
            client.get_ident(client.captureException())
        else:
            raise

if __name__ == "__main__":
    main()
