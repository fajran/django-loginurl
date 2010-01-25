from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to

from onetime.views import login

urlpatterns = patterns(''
    (r'^(?P<key>[a-z0-9+])$', login), 
    (r'^$', redirect_to, {'url': None}),
)

