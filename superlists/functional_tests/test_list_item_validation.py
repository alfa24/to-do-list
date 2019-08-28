from selenium.webdriver.common.keys import Keys

from functional_tests.base import FunctionalTest

MAX_WAIT = 10


class ItemValidationTest(FunctionalTest):
    """тест валидации элемента списка"""

    def test_cannot_add_empty_list_items(self):
        """тест: нельзя добавлять пустые элементы списка"""

        # Эдит открывает домашнюю страницу и случайно пытается отправить
        # пустой элемент списка. Она нажимает Enter на пустом поле ввода
        self.browser.get(self.live_server_url)
        self.get_item_input_box().send_keys(Keys.ENTER)

        # Домашняя страница обновляется, и появляется сообщение об ошибке,
        # которое говорит, что элементы списка не должны быть пустыми
        self.wait_for(lambda : self.browser.find_element_by_css_selector('#id_text:invalid'))

        # Она пробует снова, теперь с неким текстом для элемента, и теперь
        # это срабатывает
        self.get_item_input_box().send_keys('Купить молока')
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Купить молока')

        # Как ни странно, Эдит решает отправить второй пустой элемент списка
        # Она получает аналогичное предупреждение на странице списка
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for(lambda : self.browser.find_element_by_css_selector('#id_text:invalid'))

        # И она может его исправить, заполнив поле неким текстом
        self.get_item_input_box().send_keys('Купить чая')
        self.wait_for(lambda : self.browser.find_element_by_css_selector('#id_text:valid'))
        self.get_item_input_box().send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table('1: Купить молока')
        self.wait_for_row_in_list_table('2: Купить чая'),
