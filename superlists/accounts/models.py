import uuid

from django.contrib import auth
from django.db import models

auth.signals.user_logged_in.disconnect(auth.models.update_last_login)


class User(models.Model):
    """Модель пользователя"""

    email = models.EmailField(primary_key=True)
    REQUIRED_FIELDS = []
    USERNAME_FIELD = 'email'
    is_anonymous = False
    is_authenticated = True


class Token(models.Model):
    """Модель токена для каждого пользователя"""

    email = models.EmailField()
    uid = models.CharField(max_length=255, default=uuid.uuid4)
