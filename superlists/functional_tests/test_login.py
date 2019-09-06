import re

from django.core import mail
from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest

TEST_EMAIL = "6064233@gmail.com"
SUBJECT = "Ссылка для входа на сайт списков"


class LoginTest(FunctionalTest):
    """тест регистрации в системе"""

    def test_can_get_email_link_to_log_in(self):
        """test: можно получить ссылку регистрации по почте"""

        # Эдит заходит на сайт
        # и видит раздел войти, который предлагает ей ввести адрес электронной почты

        self.browser.get(self.live_server_url)
        self.browser.find_element_by_name('email').send_keys(TEST_EMAIL)
        self.browser.find_element_by_name('email').send_keys(Keys.ENTER)

        # Появляется сообщение, что ей на почту было выслано письмо
        self.wait_for(lambda: self.assertIn(
            "На вашу почту отправлена ссылка",
            self.browser.find_element_by_tag_name('body').text
        ))

        # Эдит проверяет свою почту и находит сообщение
        email = mail.outbox[0]
        self.assertIn(TEST_EMAIL, email.to)
        self.assertEqual(email.subject, SUBJECT)

        # Оно содержит ссылку на урл-адрес
        self.assertIn('Чтобы войти на сайт перейдите по ссылке', email.body)
        url_search = re.search(r'http://.+/.+$', email.body)
        if not url_search:
            self.fail(f'Не найдена ссылка для входа на сайт. \n{email.body}')
        url = url_search.group(0)
        self.assertIn(self.live_server_url, url)

        # Эдит нажимает на ссылка
        self.browser.get(url)

        # Она зарегистрировалась в системе!
        self.wait_to_be_logged_in(email=TEST_EMAIL)

        # Теперь она выходит из системы
        self.browser.find_element_by_link_text('Выйти').click()

        # Она вышла из системы
        self.wait_to_be_logged_out(email=TEST_EMAIL)
