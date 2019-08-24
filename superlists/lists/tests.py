from django.http import HttpRequest
from django.urls import resolve
from django.test import TestCase
from lists.views import home_page
from lists.models import Item


# Create your tests here.

class HomePageTest(TestCase):
    """тест домашней страницы"""

    def test_uses_home_template(self):
        """тест: используется домашний шаблон"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')


class ListViewTest(TestCase):
    """тест: представление списка"""

    def test_displays_all_list_items(self):
        """тест: отображаются все элементы списка"""

        Item.objects.create(text='itemey 1')
        Item.objects.create(text='itemey 2')

        response = self.client.get('/lists/edith/')

        self.assertContains(response, 'itemey 1')
        self.assertContains(response, 'itemey 2')

    def test_uses_list_template(self):
        """тест: используется шаблон списка"""
        response = self.client.get('/lists/edith/')
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
        self.assertRedirects(response, '/lists/edith/')


class ItemModelTest(TestCase):
    """тест модели списка"""

    def test_save_and_retrieving_items(self):
        """тест: сохранение и получение элементов списка"""
        first_item = Item()
        first_item.text = 'The first (ever) item'
        first_item.save()

        second_item = Item()
        second_item.text = 'Item the second'
        second_item.save()

        saved_items = Item.objects.all()
        self.assertEqual(saved_items.count(), 2)

        first_saved_item = saved_items[0]
        second_saved_item = saved_items[1]
        self.assertEqual(first_saved_item.text, 'The first (ever) item')
        self.assertEqual(second_saved_item.text, 'Item the second')
