from django.contrib.auth import get_user_model
from django.test import TestCase
from accounts.authentication import PasswordlessAuthenticationBackend

from accounts.models import Token

User = get_user_model()


class AuthenticateTest(TestCase):
    """тест модуля аутентификации пользователя"""

    def test_returns_None_if_no_such_token(self):
        """test: если нет токена,то возвращается None"""

        result = PasswordlessAuthenticationBackend().authenticate(
            'no-such-token'
        )
        self.assertIsNone(result)

    def test_returns_new_user_with_correct_email_if_token_exist(self):
        """test: возвращает пользователя, если токен существует"""

        email = "user@mail.com"
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(token.uid)
        new_user = User.objects.get(email=email)
        self.assertEqual(user, new_user)

    def test_returns_existing_user_with_correct_email_if_token_exists(self):
        """тест: возвращает существующего пользователя, если он уже зарегестрирован"""

        email = "user@mail.com"
        existing_user = User.objects.create(email=email)
        token = Token.objects.create(email=email)
        user = PasswordlessAuthenticationBackend().authenticate(token.uid)
        self.assertEqual(user, existing_user)


class GetUserTest(TestCase):
    """тест получения пользователя"""

    def test_gets_user_by_email(self):
        """test: получить пользователя по email"""

        existing_user = User.objects.create(email="user@mail.com")
        other_user = User.objects.create(email="other_user@mail.com")

        found_user = PasswordlessAuthenticationBackend().get_user("user@mail.com")
        
        self.assertEqual(existing_user, found_user)
    
    def test_returns_None_if_no_user_with_that_email(self):
        """test: Возращать None если нет пользователя с таким email"""

        found_user = PasswordlessAuthenticationBackend().get_user("user@mail.com")

        self.assertEqual(None, found_user)

