from django.contrib.auth import get_user_model

from accounts.models import Token

User = get_user_model()


class PasswordlessAuthenticationBackend(object):
    """беспарольный серверный процессор аутентификации"""

    def authenticate(self, uid):
        """аутентифицировать"""

        try:
            token = Token.objects.get(uid=uid)
            return User.objects.get(email=token.email)
        except User.DoesNotExist as e:
            return User.objects.create(email=token.email)
        except Token.DoesNotExist as e:
            return None

    def get_user(self, email):
        try:
            return User.objects.get(email=email)
        except User.DoesNotExist as e:
            return None
