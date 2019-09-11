import os
import poplib
import re
import time

from django.core import mail
from email.header import decode_header, make_header

from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest

TEST_EMAIL = "al-fa-y@yandex.ru"
SUBJECT = "Ссылка для входа на сайт списков"


class LoginTest(FunctionalTest):
    """тест регистрации в системе"""

    def wait_for_email(self, test_email, subject):
        """ожидать электронное сообщение"""

        if not self.staging_server:
            email = mail.outbox[0]
            self.assertIn(test_email, email.to)
            self.assertEqual(email.subject, subject)
            return email.body

        email_id = None
        start = time.time()
        inbox = poplib.POP3_SSL('pop.yandex.ru')

        try:
            inbox.user('al-fa-y@yandex.ru')
            inbox.pass_(os.environ['EMAIL_PASSWORD'])

            while time.time() - start < 60:
                # получить 10 самых новых сообщений
                count, _ = inbox.stat()

                for i in range(1, 10):
                    _, lines, __ = inbox.retr(i)
                    lines = [l.decode('utf-8') for l in lines]
                    msg = str(''.join(lines))
                    h = make_header(decode_header(msg))

                    if f'Subject: {subject}' in str(h):
                        email_id = i
                        body = '\n'.join(lines)
                        return body
                time.sleep(5)
        finally:
            if email_id:
                inbox.dele(email_id)

            inbox.quit()

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
        body = self.wait_for_email(TEST_EMAIL, SUBJECT)

        # Оно содержит ссылку на урл-адрес
        self.assertIn('Чтобы войти на сайт перейдите по ссылке', body)
        url_search = re.search(r'http://.+/.+$', body)
        if not url_search:
            self.fail(f'Не найдена ссылка для входа на сайт. \n{body}')
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
