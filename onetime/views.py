from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseGone
from django.contrib import auth
from django.conf import settings

from onetime import utils
from onetime.models import Key

def cleanup(request):
    utils.cleanup()
    return HttpResponse('ok', content_type='text/plain')

def login(request, key, redirect_invalid_to=None):
    user = auth.authenticate(key=key)
    if user is None:
        if redirect_invalid_to is not None:
            return HttpResponseRedirect(redirect_invalid_to)
        else:
            return HttpResponseGone()

    auth.login(request, user)

    data = Key.objects.get(key=key)
    data.update_usage()
    
    next = request.GET.get('next', None)
    if data.next is not None:
        next = data.next
    if next is None:
        next = settings.LOGIN_REDIRECT_URL

    return HttpResponseRedirect(next)

