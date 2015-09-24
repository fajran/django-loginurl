from django.conf.urls import patterns, url
from django.views.generic import RedirectView
from django.conf import settings

from loginurl.views import cleanup, login

urlpatterns = patterns('',
    (r'^cleanup/$', cleanup),
    (r'^(?P<key>[0-9A-Za-z]+-[a-z0-9-]+)/$', login), 
    url(r'^$', name='loginurl-index', view=RedirectView.as_view(
        permanent=True,
        url=settings.LOGIN_URL,
    )),
)
