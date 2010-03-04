from django.conf.urls.defaults import *
from django.views.generic.simple import redirect_to
from django.conf import settings

from loginurl.views import cleanup, login

urlpatterns = patterns('',
    (r'^cleanup/$', cleanup),
    (r'^(?P<key>[0-9A-Za-z]+-[a-z0-9-]+)/$', login), 
    url(r'^$', redirect_to, {'url': settings.LOGIN_URL}, name='loginurl-index'),
)

