#!/usr/bin/env python

import os
import tornado.web
import tornado.ioloop

from controllers import home

if __name__ == "__main__":

    # App Settings
    app_settings = dict(
        site_title=u"Awesome webapp",
        template_path=os.path.join(os.path.dirname(__file__), "views"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        xsrf_cookies=True,
        cookie_secret="A*!@#oj123!pojhas&*DYH",
        login_url="/auth/login",
        debug=True,
        # ui_modules=uimodules,
        # ui_methods=uimethods,
    )

    routes = [
    	(r"/", home.IndexHandler),
        (r"/auth/login", home.LoginHandler),
    ]


    application = tornado.web.Application(routes, **app_settings)

    print("%s server started on port %d" % ("Awesome", 8888))
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
