import tornado.ioloop
import tornado.web

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        print self.request.arguments
        self.write(self.request.arguments)

application = tornado.web.Application([
    (r"/", MainHandler),
])

def main():
    application.listen(55555)
    print "Listening callback on 55555"
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
