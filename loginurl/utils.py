import uuid
import hashlib
from datetime import datetime

from django.db.models import Q
from django.conf import settings
from django.utils.http import int_to_base36, base36_to_int

from loginurl.models import Key

def _create_token(user):
    """
    Create a unique token for a user.

    The token is created from the user id and a unique id generated
    from UUIDv4. Then both are hashed using MD5 digest algorithm.
    """
    id = '%d-%s' % (user.id, str(uuid.uuid4()))
    hash = hashlib.md5(id)
    hash.digest()
    return hash.hexdigest()

def create(user, usage_left=1, expires=None, next=None):
    """
    Create a secret login key for a user.

    Another application in your Django application can call this method to
    create a secret login key for a user. This key then can be used as a
    parameter when opening ``login`` view. See the README.rst file for example.

    By default, the key can only be used once and does not have an expiry time.
    This can be configured by setting the correct value to ``usage_left`` and
    ``expires`` properties of the key. These properties tell how many times the
    key can be used and when the key is no longer valid. Before both conditions
    are satisfied, the key is valid and can be used for authentication.

    A special value ``None`` can be used to disable one or both properties. If
    ``usage_left`` is ``None`` then the key can be used multiple times and
    ``None`` in ``expires`` property means the key will not expire.

    **Arguments**

    ``user``
        The user that the key will be created for.

    ``usage_left``
        A number that tells how many time the key can be used.

    ``expires``
        A date and time when the key is no longer valid.

    ``next``
        A path or URL where the user using this key should be redirected to.
        If this parameter is None, then the default ``settings.LOGIN_URL`` will
        be used.
    """
    token = _create_token(user)
    b36_uid = int_to_base36(user.id)
    key = '%s-%s' % (b36_uid, token)

    data = Key()
    data.user = user
    data.key = key
    data.usage_left = usage_left
    data.expires = expires
    data.next = next
    data.save()

    return data

def cleanup():
    """
    Remove expired keys.

    Keys that are no longer valid will be moved by calling this method.

    A scheduled calls should be made to this method to make the database clean.
    This can be done in at least two ways: opening the ``cleanup`` view or
    running ``loginurl_cleanup`` command from the Django's management script.
    """
    data = Key.objects.filter(Q(usage_left__lte=0) | 
                              Q(expires__lt=datetime.now()))
    if data is not None:
        data.delete()

