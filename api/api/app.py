import falcon

from .images import Resource
from .news import News

api = application = falcon.API()

images = Resource()
news = News()
api.add_route("/", news)
api.add_route("/images", images)
