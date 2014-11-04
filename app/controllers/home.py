import tornado.web

class IndexHandler(tornado.web.RequestHandler):

	def get(self):
		self.write("Hello world!")


class LoginHandler(tornado.web.RequestHandler):

	SUPPORTED_METHODS = ('GET','POST')

	def get(self):
		self.render('login.html', title='Login')


	def post(self):
		pass
