from django.conf import settings
from django.contrib.auth import BACKEND_SESSION_KEY, SESSION_KEY, get_user_model
from django.contrib.sessions.backends.db import SessionStore

from functional_tests.management.commands.create_session import create_pre_authenticated_session
from .base import FunctionalTest
from .server_tools import create_session_on_server

User = get_user_model()


class MyListsTest(FunctionalTest):
    """тест приложения “Мои списки”"""

    def test_logged_in_users_lists_are_saved_as_my_lists(self):
        """тест: списки зарегистрированных пользователей
        сохраняются как «мои списки»"""

        email = 'edith@example.com'
        self.browser.get(self.live_server_url)
        self.wait_to_be_logged_out(email)

        # Эдит является зарегистрированным пользователем
        self.create_pre_authenticated_session(email)
        self.browser.get(self.live_server_url)
        self.add_list_item('Купить печенье')
        self.add_list_item('Купить колбасу')
        first_list_url = self.browser.current_url

        # Она замечает ссылку на "Мои списки первый раз"
        self.browser.find_element_by_link_text('Мои списки').click()

        # Она видит, что ее список находится там
        # И он назвается по первому элементу
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Купить печенье')
        )
        self.browser.find_element_by_link_text('Купить печенье').click()

        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, first_list_url)
        )

        # Она решает добваить еще один список
        self.browser.get(self.live_server_url)
        self.add_list_item('Купить чай')
        second_list_url = self.browser.current_url

        # Под заголовком "Мои списки" появляется еще один списко
        self.browser.find_element_by_link_text('Мои списки').click()
        self.wait_for(
            lambda: self.browser.find_element_by_link_text('Купить чай')
        )
        self.browser.find_element_by_link_text('Купить чай').click()

        self.wait_for(
            lambda: self.assertEqual(self.browser.current_url, second_list_url)
        )

        # Она выходит из системы и "Мои списки исчезают"
        self.browser.find_element_by_link_text('Выйти').click()
        self.wait_for(lambda: self.assertEqual(
            self.browser.find_element_by_link_text('Мои списки'),
            []
        ))
