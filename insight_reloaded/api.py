import tornadoredis
import tornado.web
import tornado.ioloop
import tornado.gen
import tornado.httpserver

import json

try:
    import settings
except ImportError:
    settings = None

REDIS_HOST = getattr(settings, 'REDIS_HOST', 'localhost')
REDIS_PORT = getattr(settings, 'REDIS_PORT', 6379)
REDIS_DB = getattr(settings, 'REDIS_PORT', 0)
REDIS_QUEUE_KEY = getattr(settings, 'REDIS_QUEUE_KEY', 'insight_reloaded')

c = tornadoredis.Client(host=REDIS_HOST, port=REDIS_PORT, selected_db=REDIS_DB)
c.connect()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        params = {'url': self.get_argument("url", None),
                  'callback': self.get_argument("callback", None),}
        # Get URL
        if params['url']:
            if params['url'].startswith('/'):
                params['url'] = '%s://%s%s' % (self.request.protocol, self.request.host, url)
        else:
            raise tornado.web.HTTPError(404, 'Input file not found')
        
        # Max number of pages to compile
        try:
            params['max_previews'] = int(self.get_argument('pages', 20))
        except:
            params['max_previews'] = 20

        params['crop'] = self.get_argument('crop', False) and True

        message = json.dumps(params)
        c.rpush(REDIS_QUEUE_KEY, message)
    
        self.write("Job added to queue.")


application = tornado.web.Application([
    (r"/", MainHandler),
])

def main():
    print "Launch tornado ioloop"
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
