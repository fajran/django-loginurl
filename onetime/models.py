from datetime import datetime

from django.db import models
from django.contrib.auth.models import User

class Key(models.Model):
    """
    A simple key store.
    """
    user = models.ForeignKey(User)
    key = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)
    usage_left = models.IntegerField(null=True, default=1)
    expires = models.DateTimeField(null=True)
    next = models.CharField(null=True, max_length=200)

    def __unicode__(self):
        return '%s (%s)' % (self.key, self.user.username)

    def is_valid(self):
        """
        Check if the key is valid.

        Key validation checks the value of ``usage_left`` and ``expires``
        properties of the key. If both are ``None`` then the key is always
        valid.
        """
        if self.usage_left is not None and self.usage_left <= 0:
            return False
        if self.expires is not None and self.expires < datetime.now():
            return False
        return True

    def update_usage(self):
        """
        Update key usage counter.

        This only relevant if the ``usage_left`` property is used.
        """
        if self.usage_left is not None and self.usage_left > 0:
            self.usage_left -= 1
            self.save()

