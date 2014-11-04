import os
import model
import peewee
import tornado
import tornado.web

from tornado.options import options
from tornado.web import RequestHandler

try:
	import simplejson as json
except ImportError:
	import json


AJAX_HEADERS = ('X-PJAX','X-Requested-With',)

BASE_DIR = os.path.dirname(os.path.realpath(__file__))
PJAX_TEMPLATE = '''
{{% extends "{0}/views/vanilla/layout.html" %}}
{{% include "{0}/views/vanilla/{1}" %}}
'''

class BaseHandler(tornado.web.RequestHandler):

    def initialize(self):
        self.session = None
        self.is_ajax = False

    def prepare(self):
        self.domain = ("%s://%s" %
          (self.request.protocol,
          self.request.host,)
        )
        self.is_ajax = any(hdr in self.request.headers for hdr in AJAX_HEADERS)

    def get_current_user(self):
        """
        Load the user from the session token
        Used by tornado.web.authenticated decorator
        """
        signed_token = self.get_argument('token', None)
        # If not, try the cookie
        signed_token = signed_token or self.get_cookie('token', None)
        # If we have a token
        if signed_token:
            # Decode the token
            token = self.get_secure_cookie('token', signed_token)
            if token:
                # Verify if the session exists and is valid
                self.session = model.Session.load(token)
                if self.session:
                    return self.session.user
            return None
        # Try basic auth
        else:
            return self.basic_auth()

    def basic_auth(self):
        auth_header = self.request.headers.get("Authorization", None)
        if auth_header is not None and auth_header.startswith('Basic'):
            try:
                auth_decoded = base64.decodestring(auth_header[6:])
                email, password = auth_decoded.split(':', 2)
                # Validate and return user
                return model.Session.authenticate(
                    email=email, password=password)
            except Exception:
                return None
        return None


    def on_finish(self):
        """ Do something when the request has been processed """
        pass


    def render(self, template_name, **kwargs):
        # Check if the request is through PJAX
        # If so, render only the content and not the template
        # Unfortunately, tornado doesn't allow conditional inheritance
        # So this is a workaround
        if self.is_ajax:
            # If we are using pjax, the title block in the
            # template is of no use. To update the document
            # title, pass in another key called page_title
            # in the kwargs, which will then be set as a HTTP
            # header. The PJAX handler will then update the title
            title = kwargs.get('page_title',
                template_name.replace(".html","").replace("_"," ").title())
            self.set_header('X-PAGE-TITLE', title)

            super(BaseHandler, self).render(template_name, **kwargs)


    def redirect(self, url):
        if not self.is_ajax:
            super(BaseHandler, self).redirect(url)
        else:
            self.set_status(200, reason="XHR-Redirect")
            self.finish({
                'redirect_to': url
                })

    def _get_loader(self):
        template_path = self.get_template_path()
        with RequestHandler._template_loader_lock:
            if template_path not in RequestHandler._template_loaders:
                loader = self.create_template_loader(template_path)
                RequestHandler._template_loaders[template_path] = loader
            else:
                loader = RequestHandler._template_loaders[template_path]
        return loader


    def render_pjax(self, template_name, **kwargs):
        if not self.is_ajax:
            loader = self._get_loader()
            template = PJAX_TEMPLATE.format(BASE_DIR, template_name)
            namespace = self.get_template_namespace()
            namespace.update(kwargs)
            self.write(tornado.template.Template(
                template, loader=loader).generate(**namespace)
            )
        else:
            self.write(self.render_string(template_name, **kwargs))


def query_to_json(self):
	if isinstance(self, peewee.SelectQuery):
		return [o.to_dict() for o in self]

if not hasattr(peewee.SelectQuery, "to_dict"):
	setattr(peewee.SelectQuery, "to_dict", query_to_json)

class QueryEncoder(json.JSONEncoder):
	def default(self, obj):
		if isinstance(obj, peewee.SelectQuery):
			return [o.to_dict() for o in obj]
		elif hasattr(obj, "_data"):
			return obj._data
		return json.JSONEncoder.default(self, obj)

json_dumper = QueryEncoder()

__all__ = [
    "BaseModel",
    'BaseHandler',
]
