from django.test import TestCase

import accounts.views
from unittest.mock import patch, call

from accounts.models import Token


class SendLoginEmailViewTest(TestCase):
    """тест представления, которое отправляет сообщение для входа"""

    def test_redirects_to_home_page(self):
        """тест: переадресация на главную страницу"""

        response = self.client.post('/accounts/send_login_email', data={
            'email': 'user@mail.com'
        })

        self.assertRedirects(response, '/')

    @patch('accounts.views.send_mail')
    def test_sends_mail_to_address_from_post(self, mock_send_mail):
        """test: отправка email из пост запроса"""

        self.send_mail_called = False

        response = self.client.post('/accounts/send_login_email', data={
            'email': 'user@mail.com'
        })

        self.assertTrue(mock_send_mail.called)
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertEqual(subject, 'Ссылка для входа на сайт списков')
        self.assertEqual(from_email, 'al-fa-y@yandex.ru')
        self.assertEqual(to_list, ['user@mail.com'])

    def test_adds_success_messages(self):
        """test: добавляется сообщение об успехе"""

        response = self.client.post('/accounts/send_login_email', data={
            'email': 'user@mail.com'
        }, follow=True)

        message = list(response.context['messages'])[0]
        self.assertEqual(message.message, 'На вашу почту отправлена ссылка')

    def test_creates_login_associated_with_email(self):
        """test: создается токен связанный с email"""

        response = self.client.post('/accounts/send_login_email', data={
            'email': 'user@mail.com'
        })

        token = Token.objects.first()
        self.assertEqual(token.email, 'user@mail.com')

    @patch('accounts.views.send_mail')
    def test_sends_link_to_login_using_token_uid(self, mock_send_mail):
        """тест: отправка ссылки на вход"""

        response = self.client.post('/accounts/send_login_email', data={
            'email': 'user@mail.com'
        })

        token = Token.objects.first()
        expected_url = f'http://testserver/accounts/login?token={token.uid}'
        (subject, body, from_email, to_list), kwargs = mock_send_mail.call_args
        self.assertIn(expected_url, body)


@patch('accounts.views.auth')
class LoginViewTest(TestCase):
    """тест представления логина"""

    def test_redirects_to_home_page(self, mock_auth):
        """тест: переадресация на главную страницу после входа"""

        response = self.client.get('/accounts/login?token=123')
        self.assertRedirects(response, '/')

    def test_calls_authenticate_with_uid_from_get_request(self, mock_auth):
        """тест: вызывается authenticate с uid из GET-запроса"""

        self.client.get('/accounts/login?token=abcd123')
        self.assertEqual(
            mock_auth.authenticate.call_args, call(uid='abcd123')
        )

    def test_calls_auth_login_with_user_if_there_is_one(self, mock_auth):
        '''тест: вызывается auth_login с пользователем, если такой имеется'''
        response = self.client.get('/accounts/login?token=abcd123')
        self.assertEqual(
            mock_auth.login.call_args,
            call(response.wsgi_request, mock_auth.authenticate.return_value)
        )

    def test_does_not_login_if_user_is_not_authenticated(self, mock_auth):
        """тест: не регистрируется в системе, если пользователь
        Не аутентифицирован"""
        mock_auth.authenticate.return_value = None
        self.client.get('/accounts/login?token=abcd123')
        self.assertEqual(mock_auth.login.called, False)
