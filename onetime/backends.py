from django.contrib.auth.models import User

from onetime.models import Key

class OneTimeBackend:
    def authenticate(self, key):
        data = Key.objects.get(key=key)
        if data is None:
            None

        if not data.is_valid():
            return None

        return data.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
