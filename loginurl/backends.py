from django.contrib.auth.models import User

from loginurl.models import Key

class LoginUrlBackend:
    """
    Authentication backend that checks the given ``key`` to a record in the
    ``Key`` model. If the record is found, then ``is_valid()`` method is called
    to check if the key is still valid.
    """
    def authenticate(self, key):
        """
        Check if the key is valid.
        """
        data = Key.objects.filter(key=key)
        if len(data) == 0:
            return None

        data = data[0]
        if not data.is_valid():
            return None

        return data.user

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
        
