import uuid
import hashlib
from datetime import datetime

from django.db.models import Q
from django.conf import settings
from django.utils.http import int_to_base36, base36_to_int

from onetime.models import Key

def _create_token(user):
    id = '%d-%s' % (user.id, str(uuid.uuid4()))
    hash = hashlib.md5(id)
    hash.digest()
    return hash.hexdigest()

def create(user, usage_left=1, expires=None, next=None):
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
    data = Key.objects.filter(Q(usage_left__lte=0) | 
                              Q(expires__lt=datetime.now()))
    if data is not None:
        data.delete()

