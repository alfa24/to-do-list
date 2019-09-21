import unittest
from unittest import skip
from unittest.mock import patch, Mock

from django.contrib.auth import get_user_model
from django.http import HttpRequest
from django.test import TestCase
from django.utils.html import escape

from lists.forms import ItemForm, EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR, ExistingListItemForm
from lists.models import Item, List
from lists.views import new_list

User = get_user_model()


class HomePageTest(TestCase):
    """тест домашней страницы"""

    def test_uses_home_template(self):
        """тест: используется домашний шаблон"""
        response = self.client.get('/')
        self.assertTemplateUsed(response, 'home.html')

    def test_uses_item_form(self):
        """test: домашняя страница использует форму для элемента"""

        response = self.client.get('/')
        self.assertIsInstance(response.context['form'], ItemForm)


class ListViewTest(TestCase):
    """тест: представление списка"""

    def post_invalid_inputs(self):
        """отправляет недопустимы ввод"""

        list_ = List.objects.create()
        return self.client.post(
            f'/lists/{list_.id}/',
            data={'text': ''}
        )

    def test_displays_only_items_for_that_list(self):
        """тест: отображаются элементы только для этого списка"""

        correct_list = List.objects.create()
        Item.objects.create(text='itemey 1', list=correct_list)
        Item.objects.create(text='itemey 2', list=correct_list)

        other_list = List.objects.create()
        Item.objects.create(text='other list itemey 1', list=other_list)
        Item.objects.create(text='other list itemey 2', list=other_list)

        response = self.client.get(f'/lists/{correct_list.id}/')

        self.assertIsInstance(response.context['form'], ExistingListItemForm)
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
        self.client.post('/lists/new', data={'text': "A new list item"})
        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, "A new list item")

    def test_redirects_after_POST(self):
        """тест: редирект после пост запроса"""
        response = self.client.post('/lists/new', data={'text': "A new list item"})
        list_ = List.objects.first()
        self.assertRedirects(response, f'/lists/{list_.id}/')

    def test_passes_correct_list_to_template(self):
        """тест: передает правильный шаблон списка"""

        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.get(f'/lists/{correct_list.id}/')
        self.assertEqual(response.context['list'], correct_list)

    def test_POST_redirects_to_list_view(self):
        """тест: POST запрос переадресует в представление списка"""

        other_list = List.objects.create()
        correct_list = List.objects.create()

        response = self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'Новая запись в существующем списке'}
        )

        self.assertRedirects(response, f'/lists/{correct_list.id}/')

    def test_can_save_a_POST_request_to_an_existing_list(self):
        """тест: можно сохранить пост-запрос в существующий список"""

        other_list = List.objects.create()
        correct_list = List.objects.create()

        self.client.post(
            f'/lists/{correct_list.id}/',
            data={'text': 'Новая запись в существующем списке'}
        )

        self.assertEqual(Item.objects.count(), 1)
        new_item = Item.objects.first()
        self.assertEqual(new_item.text, 'Новая запись в существующем списке')
        self.assertEqual(new_item.list, correct_list)

    def test_displays_item_form(self):
        """test: отображение формы для элемента"""

        list_ = List.objects.create()
        response = self.client.get(f'/lists/{list_.id}/')
        self.assertIsInstance(response.context['form'], ItemForm)
        self.assertContains(response, 'name="text"')

    def test_for_invalid_input_nothing_saved_to_db(self):
        """test: при недопустимом вводе ничего не сохраняется в БД"""

        self.post_invalid_inputs()
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_list_template(self):
        """test: при недопустимом вводе отображается шаблон списка"""

        response = self.post_invalid_inputs()
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'list.html')

    def test_for_invalid_input_passes_form_to_template(self):
        """test: при недопустимом вводе форма передается в шаблон"""

        response = self.post_invalid_inputs()
        self.assertIsInstance(response.context['form'], ExistingListItemForm)

    def test_for_invalid_input_shows_error_on_page(self):
        """test: при недопустимом вводе отображается ошибка"""

        response = self.post_invalid_inputs()
        self.assertContains(response, escape(EMPTY_ITEM_ERROR))

    def test_duplicate_item_validation_errors_end_up_on_lists_page(self):
        """тест: ошибки валидации повторяющегося элемента
        оканчиваются на странице списков"""

        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='textey')
        response = self.client.post(
            f'/lists/{list1.id}/',
            data={'text': 'textey'}
        )
        expected_error = escape(DUPLICATE_ITEM_ERROR)
        self.assertContains(response, expected_error)
        self.assertTemplateUsed(response, 'list.html')
        self.assertEqual(Item.objects.all().count(), 1)


class NewListViewIntegratedTest(TestCase):
    """тест нового списка"""

    def test_invalid_list_items_arent_saved(self):
        """тест: сохраняются недопустимые элементы списка"""

        self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(List.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)

    def test_for_invalid_input_renders_home_template(self):
        """test: при недопустимом вводе отображает домашнюю страницу"""

        response = self.client.post('/lists/new', data={'text': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_validation_errors_are_shown_on_home_page(self):
        """test: ошибки валидации отображаются на главкной странице"""

        response = self.client.post('/lists/new', data={'text': ''})
        expected_error = escape('Элементы списка не должны быть пустыми')
        self.assertContains(response, expected_error)

    def test_for_invalid_input_passes_form_to_template(self):
        """test: При недопустимом вводе форма передается в шаблон"""

        response = self.client.post('/lists/new', data={'text': ''})
        self.assertIsInstance(response.context['form'], ItemForm)

    def test_can_save_a_POST_request(self):
        """test: может сохранить пост запрос"""
        pass

    @patch('lists.views.NewListForm')
    def test_list_owner_is_saved_if_user_authenticated(
            self, mockNewListFormClass
    ):
        """тест: владелец сохраняется, если пользователь аутентифицирован"""

        user = User.objects.create(email="a@b.ru")
        self.client.force_login(user)

        mock_list = mockNewListFormClass.return_value

        self.client.post('/lists/new', data={'text': 'new item'})

        mock_list.save.assert_called_once_with(owner=user)


@patch('lists.views.NewListForm')
class NewListViewUnitTest(unittest.TestCase):
    """модульный тест нового представления списка"""

    def setUp(self):
        """установка"""

        self.request = HttpRequest()
        self.request.POST['text'] = 'new list item'
        self.request.user = Mock()

    def test_passes_POST_data_to_NewListForm(self, mockNewListForm):
        """тест: передаются POST-данные в новую форму списка"""

        new_list(self.request)
        mockNewListForm.assert_called_once_with(data=self.request.POST)

    def test_saves_form_with_owner_if_form_valid(self, mockNewListForm):
        """тест: сохраняет форму с владельцем, если форма допустима"""

        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        new_list(self.request)
        mock_form.save.assert_called_once_with(owner=self.request.user)

    @patch('lists.views.redirect')
    def test_redirects_to_form_returned_object_if_form_valid(
            self, mock_redirect, mockNewListForm
    ):
        """тест: переадресует в возвращаемый формой объект, если форма допустима"""

        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = True
        response = new_list(self.request)
        self.assertEqual(response, mock_redirect.return_value)
        mock_redirect.assert_called_once_with(mock_form.save.return_value)

    @patch('lists.views.render')
    def test_renders_home_template_with_form_if_form_invalid(
            self, mock_render, mockNewListForm
    ):
        """тест: отображает домашний шаблон с формой, если форма недопустима"""

        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        response = new_list(self.request)
        self.assertEqual(response, mock_render.return_value)
        mock_render.assert_called_once_with(
            self.request, 'home.html', {'form': mock_form}
        )

    def test_does_not_save_if_form_invalid(self, mockNewListForm):
        """тест: не сохраняет, если форма недопустима"""

        mock_form = mockNewListForm.return_value
        mock_form.is_valid.return_value = False
        new_list(self.request)
        self.assertFalse(mock_form.save.called)


class MyListsTest(TestCase):

    def test_my_lists_url_renders_my_lists_template(self):
        """тест: url-адрес использует правильный шаблон моих списков"""

        User.objects.create(email="user@mail.com")
        response = self.client.get('/lists/users/user@mail.com/')
        self.assertTemplateUsed(response, 'my_lists.html')

    def test_passes_correct_owner_to_template(self):
        """тест: передается правильный владелец в шаблон"""

        User.objects.create(email="user@mail.com")
        correct_user = User.objects.create(email="correct_user@mail.com")
        response = self.client.get('/lists/users/correct_user@mail.com/')
        self.assertEqual(response.context['owner'], correct_user)


class ShareListTest(TestCase):
    """тест расшаривания списков"""

    def test_post_redirects_to_list_page(self):
        """test: POST запрос переадресуется на страницу списка"""

        list_ = List.create_new("Купитьс чая")
        response = self.client.post(f"/lists/{list_.id}/share")
        self.assertRedirects(response, f'/lists/{list_.id}/')

    def test_email_save_in_share_with(self):
        """test: емаил сохраняется в списке "поделился c"""

        friend = User.objects.create(email="friend_mail@mail.com")
        list_ = List.create_new("Купитьс чая")
        self.client.post(f"/lists/{list_.id}/share", data={"sharee": friend.email})
        self.assertIn(friend, list_.shared_with.all())
        print(friend.available_lists.all(), list_.shared_with.all())

        
        