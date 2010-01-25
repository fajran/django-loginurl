from django.db import models
from django.contrib.auth.models import User

class Key(models.Model):
    user = models.ForeignKey(User)
    key = models.CharField(max_length=40)
    created = models.DateTimeField(auto_now_add=True)
    usage_left = models.IntegerField(null=True, default=1)
    expires = models.DateTimeField(null=True)
    next = models.CharField(null=True, max_length=200)

