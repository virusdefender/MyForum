import sae
from MyForum import wsgi

application = sae.create_wsgi_app(wsgi.application)

