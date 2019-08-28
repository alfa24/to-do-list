from django.test import TestCase
from django.utils.html import escape

from lists.models import Item, List


class HomePageTest(TestCase):
    """тест домашней страницы"""

    def test_uses_home_template(self):
        """тест: используется домашний шаблон"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class ListViewTest(TestCase):
    """тест: представление списка"""

    def test_displays_only_items_for_that_list(self):
        """тест: отображаются элементы только для этого списка"""

        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text='other list itemey 1', list=other_list)
        Item.objects.create(text='other list itemey 2', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')
        self.assertNotContains(response, 'other list itemey 1')
        self.assertNotContains(response, 'other list itemey 2')

    def test_uses_list_template(self):
        """тест: используется шаблон списка"""
        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertTemplateUsed(response, 'list.html')

    def test_can_save_a_POST_request(self):
        """тест: сохранить пост запрос"""
        self.client.post('/lists/new', data={'item_text': "A new list item"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirects_after_POST(self):
        """тест: редирект после пост запроса"""
        response = self.client.post('/lists/new', data={'item_text': "A new list item"})
        list_ = List.objects.first()
        self.assertRedirects(response, f'/lists/{list_.id}/')

    def test_passes_correct_list_to_template(self):
        """тест: передает правильный шаблон списка"""

        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)


class NewItemTest(TestCase):
    """тест: тест нового элемента списка"""

    def test_can_save_a_POST_request_to_an_existing_list(self):
        """тест: можно сохранить пост-запрос в существующий список"""

        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/add_item',
            data={'item_text': 'Новая запись в существующем списке'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'Новая запись в существующем списке')
        self.assertEqual(new_item.list, correct_list)

    def test_redirects_to_list_view(self):
        """тест: переадресация в представление списка"""

        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/add_item',
            data={'item_text': 'Новая запись в существующем списке'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')


class NewListTest(TestCase):
    """тест нового списка"""

    def test_validation_errors_are_sent_back_to_home_page_template(self):
        """тест: ошибки валидации отсылаются назад в шаблон
        домашней страницы"""

        response = self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        expected_error = escape('Элементы списка не должны быть пустыми')
        self.assertContains(response, expected_error)

    def test_invalid_list_items_arent_saved(self):
        """тест: сохраняются недопустимые элементы списка"""

        self.client.post('/lists/new', data={'item_text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
