from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest
from lists.forms import DUPLICATE_ITEM_ERROR

MAX_WAIT = 10


class ItemValidationTest(FunctionalTest):
    """тест валидации элемента списка"""

    def get_error_element(self):
        """получить элемент с ошибкой"""

        return self.browser.find_element_by_css_selector('.has-error')

    def test_cannot_add_empty_list_items(self):
        """тест: нельзя добавлять пустые элементы списка"""

        # Эдит открывает домашнюю страницу и случайно пытается отправить
        # пустой элемент списка. Она нажимает Enter на пустом поле ввода
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys(Keys.ENTER)

        # Домашняя страница обновляется, и появляется сообщение об ошибке,
        # которое говорит, что элементы списка не должны быть пустыми
        self.wait_for(lambda: self.browser.find_element_by_css_selector('#id_text:invalid'))

        # Она пробует снова, теперь с неким текстом для элемента, и теперь
        # это срабатывает
        self.get_item_input_box().send_keys('Купить молока')
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Купить молока')

        # Как ни странно, Эдит решает отправить второй пустой элемент списка
        # Она получает аналогичное предупреждение на странице списка
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for(lambda: self.browser.find_element_by_css_selector('#id_text:invalid'))

        # И она может его исправить, заполнив поле неким текстом
        self.get_item_input_box().send_keys('Купить чая')
        self.wait_for(lambda: self.browser.find_element_by_css_selector('#id_text:valid'))
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Купить молока')
        self.wait_for_row_in_list_table('2: Купить чая')

    def test_cannot_add_duplicate_item(self):
        """test: нельзя добавлять одинаковые элементы списка"""

        # Эдит открывает страницу
        self.browser.get(self.live_server_url)

        # И начинает новый список
        self.get_item_input_box().send_keys('Купить молока')
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Купить молока')

        # Она случайно пытается завести одинаковый элемент
        self.get_item_input_box().send_keys('Купить молока')
        self.get_item_input_box().send_keys(Keys.ENTER)

        # Она видит сообщение об ошибке
        self.wait_for(lambda: self.assertIn(
            DUPLICATE_ITEM_ERROR,
            self.get_error_element().text
        ))

    def test_error_messages_are_cleared_on_input(self):
        """test: сообщения об ошибках очищаются при вводе"""

        # Эдит начинает новый список и вызывает ошибку валидации
        self.get_item_input_box().send_keys('Купить молока')
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Купить молока')
        self.get_item_input_box().send_keys('Купить молока')
        self.get_item_input_box().send_keys(Keys.ENTER)

        self.wait_for(lambda: self.assertTrue(
            self.get_error_element().is_displayed()
        ))

        # Она начинает набиравть в поле ввода, чтобы исправить ошибку
        self.get_item_input_box().send_keys('а')

        # Она довольна что исчезает сообщение об ошибке
        self.wait_for(lambda: self.assertFalse(
            self.get_error_element().is_displayed()
        ))
