from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.test import TestCase

from lists.models import Item, List

User = get_user_model()


class ListModelTest(TestCase):
    """тест модели списка"""

    def test_get_absolute_url(self):
        """тест: получить абсолютный урл списка"""
        list_ = List.objects.create()
        self.assertEqual(f'/lists/{list_.id}/', list_.get_absolute_url())

    def test_lists_can_have_owners(self):
        """test: списки могут иметь владельцев"""

        user = User.objects.create(email="user@mail.com")
        list_ = List.objects.create(owner=user)
        self.assertIn(list_, user.list_set.all())

    def test_list_owner_is_optional(self):
        """test: владелец списка является необязательным"""

        List.objects.create()  # не должно вызывать исключение


class ItemModelTest(TestCase):
    """тест модели элемента списка"""

    def test_default_text(self):
        """test: текст элемента по умолчанию"""

        item = Item()
        self.assertEqual(item.text, '')

    def test_item_related_to_list(self):
        """test: Элемент связан со списком"""

        list_ = List.objects.create()

        item = Item()
        item.list = list_
        item.save()

        self.assertIn(item, list_.item_set.all())

    def test_can_not_save_empty_list_items(self):
        """тест: нельзя добавлять пустые элементы списка"""

        list_ = List.objects.create()
        item = Item.objects.create(list=list_, text='')

        with self.assertRaises(ValidationError):
            item.save()
            item.full_clean()

    def test_duplicate_items_are_invalid(self):
        """test: дубликаты списка недопустимы"""

        list_ = List.objects.create()
        Item.objects.create(list=list_, text='new item')

        with self.assertRaises(IntegrityError):
            item = Item(list=list_, text='new item')
            item.save()

    def test_can_save_same_item_to_different_list(self):
        """test: одинаковый элемент можно сохранить в разные списки"""

        list1 = List.objects.create()
        list2 = List.objects.create()
        Item.objects.create(list=list1, text='new item')

        item = Item(list=list2, text='new item')

        # не должен поднять ошибку
        item.full_clean()

    def test_list_ordering(self):
        """test: сортировка списка"""

        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='new item 1')
        item2 = Item.objects.create(list=list1, text='item 2')
        item3 = Item.objects.create(list=list1, text='3')

        self.assertEqual(list(Item.objects.all()), [item1, item2, item3])

    def test_string_representation(self):
        """test: строковое представление списка"""

        list1 = List.objects.create()
        item1 = Item.objects.create(list=list1, text='new item 1')
        self.assertEqual(str(item1), 'new item 1')
