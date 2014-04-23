from django.conf.urls import patterns, url
from django.views.generic import RedirectView
from django.conf import settings

from loginurl.views import cleanup, login

urlpatterns = patterns('',
    (r'^cleanup/$', cleanup),
    (r'^(?P<key>[0-9A-Za-z]+-[a-z0-9-]+)/$', login), 
    url(r'^$', RedirectView.as_view(url=settings.LOGIN_URL), name='loginurl-index'),
)
