from datetime import datetime

from django.http import HttpResponseRedirect, HttpResponseGone
from django.shortcuts import get_object_or_404
from django.contrib.auth import login
from django.conf import settings

from onetime.models import Key

def login(request, key):
    data = get_object_or_404(Key, key=key)

    if data.usage_left is not None and data.usage_left == 0:
        return HttpResponseGone()
    if data.expires is not None and data.expires < datetime.now():
        return HttpResponseGone()

    if data.usage_left is not None:
        data.usage_left -= 1
        data.save()

    login(request, data.user)

    next = request.GET.get('next', None)
    if data.next is not None:
        next = data.next
    if next is None:
        next = settings.LOGIN_REDIRECT_URL

    return HttpResponseRedirect(next)

