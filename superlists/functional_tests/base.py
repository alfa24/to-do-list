import os
import time

from django.conf import settings

from functional_tests.management.commands.create_session import create_pre_authenticated_session
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.keys import Keys

from .server_tools import reset_database
from .server_tools import create_session_on_server

MAX_WAIT = 10


def wait(fn):
    """декоратор для явного ожидания работы функции"""

    def modified_fn(*args, **kwargs):
        start_time = time.time()
        while True:
            try:
                # поппытка выполнить функцию
                return fn(*args, **kwargs)

            # если ошибка сравнения или ошибка браузера
            except (AssertionError, WebDriverException) as e:

                # если превышен таймаут, то ошибка
                if time.time() - start_time > MAX_WAIT:
                    raise e

                # если таймаут не вышел, то попробуем выполнить еще разок
                time.sleep(0.5)

    return modified_fn


class FunctionalTest(StaticLiveServerTestCase):
    """функциональный тест"""

    def make_browser(self):
        return webdriver.Chrome('/usr/bin/chromedriver')

    def create_pre_authenticated_session(self, email):
        """создать предварительно аутентифицированный сеанс"""

        if self.staging_server:
            session_key = create_session_on_server(self.staging_server, email)
        else:
            session_key = create_pre_authenticated_session(email)

        # # установить cookie, которые нужны для первого посещения домена.
        # # страницы 404 загружаются быстрее всего!
        self.browser.get(self.live_server_url + "/404_no_such_url/")
        self.browser.add_cookie(dict(
            name=settings.SESSION_COOKIE_NAME,
            value=session_key,
            path='/',
        ))

    # todo Почистить функции wait for
    def setUp(self) -> None:
        self.browser = self.make_browser()
        self.staging_server = os.environ.get('STAGING_SERVER')
        if self.staging_server:
            self.live_server_url = f'http://{self.staging_server}'
            reset_database(self.staging_server)

    def tearDown(self) -> None:
        self.browser.quit()

    def wait_for_row_in_list_table(self, row_text):
        start_time = time.time()

        while True:
            try:
                table = self.browser.find_element_by_id('id_list_table')
                rows = table.find_elements_by_tag_name('tr')
                self.assertIn(row_text, [row.text for row in rows])
                return
            except (AssertionError, WebDriverException) as e:
                if time.time() - start_time > MAX_WAIT:
                    raise e
                time.sleep(0.5)

    @wait
    def wait_for(self, fn):
        """ожидать"""
        return fn

    def get_item_input_box(self):
        """получить поле вводя для элемента"""

        return self.browser.find_element_by_id('id_text')

    def wait_to_be_logged_in(self, email):
        """ожидать входа в систему"""

        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Выйти')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertIn(email, navbar.text)

    def wait_to_be_logged_out(self, email):
        """ожидать выхода из системы"""

        self.wait_for(
            lambda: self.browser.find_element_by_name('email')
        )
        navbar = self.browser.find_element_by_css_selector('.navbar')
        self.assertNotIn(email, navbar.text)

    def add_list_item(self, item_text):
        """Добавить элемент списка"""

        num_rows = len(self.browser.find_elements_by_css_selector('#id_list_table tr'))
        inputbox = self.get_item_input_box()
        inputbox.send_keys(item_text)
        inputbox.send_keys(Keys.ENTER)
        item_number = num_rows + 1
        self.wait_for_row_in_list_table(f'{item_number}: {item_text}')
