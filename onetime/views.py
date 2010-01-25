from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseGone
from django.contrib import auth
from django.conf import settings

from onetime import utils
from onetime.models import Key

def cleanup(request):
    utils.cleanup()
    return HttpResponse('ok', content_type='text/plain')

def login(request, key, login_url=None):
    next = request.GET.get('next', None)
    if next is None:
        next = settings.LOGIN_REDIRECT_URL

    user = auth.authenticate(key=key)
    if user is None:
        url = settings.LOGIN_URL
        if next is not None:
            url = '%s?next=%s' % (url, next)
        return HttpResponseRedirect(url)

    auth.login(request, user)

    data = Key.objects.get(key=key)
    data.update_usage()

    if data.next is not None:
        next = data.next
    
    return HttpResponseRedirect(next)

