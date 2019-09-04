from django.contrib import auth
from django.contrib.auth import get_user_model
from django.test import TestCase
from accounts.models import Token

User = get_user_model()


class UserModelTest(TestCase):
    """тест модели пользователя"""

    def test_user_is_valid_with_email_only(self):
        """тест: пользователь допустим только с email"""

        user = User(email="test@mail.ru")
        user.full_clean()  # не должно поднять исключение

    def test_email_is_primary_key(self):
        """test: email является первичным ключом"""

        user = User(email="test@mail.ru")
        self.assertIn(user.pk, "test@mail.ru")

    def test_no_problem_with_auth_login(self):
        """тест: проблем с auth_login нет"""

        user = User.objects.create(email='edith@example.com')
        user.backend = ''
        request = self.client.request().wsgi_request
        auth.login(request, user)  # не должно поднять исключение


class TokenModelTest(TestCase):
    """Тест модели маркера"""
    
    def test_links_user_with_auto_generated_uid(self):
        """test: связывает пользователя с уникальным токеном"""
        
        token1 = Token.objects.create(email="user@mail.com")
        token2 = Token.objects.create(email="user@mail.com")

        self.assertNotEqual(token1.uid, token2.uid)
