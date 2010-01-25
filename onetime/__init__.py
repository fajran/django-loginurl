import uuid
import hashlib

from django.db.models import Q
from django.conf import settings

from onetime.models import Key

def create(user, usage_left=1, expires=None, next=None):
    id = str(uuid.uuid4())
    hash = hashlib.sha1(id)
    hash.digest()
    key = hash.hexdigest()

    data = Key()
    data.user = user
    data.key = key
    data.usage_left = usage_left
    data.expires = expires
    data.next = next
    data.save()

    return key

def cleanup():
    data = Key.objects.filter(Q(usage_left__lte=0) | 
                              Q(expires__lt=datetime.now()))
    data.delete()

