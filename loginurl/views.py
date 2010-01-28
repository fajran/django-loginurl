from datetime import datetime

from django.http import HttpResponse, HttpResponseRedirect, HttpResponseGone
from django.contrib import auth
from django.conf import settings

from loginurl import utils
from loginurl.models import Key

def cleanup(request):
    """
    Remove expired keys.
    """
    utils.cleanup()
    return HttpResponse('ok', content_type='text/plain')

def login(request, key):
    """
    Log in using a key.

    When a visitor opens this view with a valid key, the visitor will be logged
    in using the user associated with the key.

    When the log in is successful, the usage counter in the key is updated. If
    the key is really a one time key, the next usage of the key will be
    considered invalid.

    A successful request will redirect the visitor to the URL associated with
    the key. If the URL is ``None``, a ``next`` parameter in the query string
    will be used. If it also does not exist, the default
    ``settings.LOGIN_REDIRECT_URL`` will be used.

    Visitor with an invalid key will be redirected to the default log in page
    specified in ``settings.LOGIN_REDIRECT_URL``. Any value in the ``next``
    parameter in the query string will be also forwarded.
    """
    next = request.GET.get('next', None)
    if next is None:
        next = settings.LOGIN_REDIRECT_URL

    # Validate the key through the standard Django's authentication mechanism.
    # It also means that the authentication backend of this django-loginurl
    # application has to be added to the authentication backends configuration.
    user = auth.authenticate(key=key)
    if user is None:
        url = settings.LOGIN_URL
        if next is not None:
            url = '%s?next=%s' % (url, next)
        return HttpResponseRedirect(url)

    # The key is valid, then now log the user in.
    auth.login(request, user)

    # Update key usage.
    data = Key.objects.get(key=key)
    data.update_usage()

    if data.next is not None:
        next = data.next
    
    return HttpResponseRedirect(next)

