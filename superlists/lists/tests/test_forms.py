from django.test import TestCase
from lists.forms import ItemForm, ExistingListItemForm, EMPTY_ITEM_ERROR, DUPLICATE_ITEM_ERROR
from lists.models import List, Item


class ItemFormTest(TestCase):
    """тест формы для элемента списка"""

    def test_form_renders_item_text_inputs(self):
        """тест: форма отображает текстовое поле ввода"""

        form = ItemForm()
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())
        self.assertIn('class="form-control input-lg"', form.as_p())

    def test_validation_for_blank_items(self):
        """test: валидация формы для пустых элементов"""

        form = ItemForm(data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [EMPTY_ITEM_ERROR]
        )

    def test_form_save_handles_saving_to_a_list(self):
        """test: метод формы обрабатывает сохранения в список"""

        list_ = List.objects.create()
        form = ItemForm(data={
            'text': 'do me',
        })

        new_item = form.save(for_list=list_)
        self.assertEqual(new_item, Item.objects.first())
        self.assertEqual(new_item.text, 'do me')
        self.assertEqual(new_item.list, list_)


class ExistingListItemFormTest(TestCase):
    """тест формы для элемента существующего списка"""

    def test_form_renders_item_text_inputs(self):
        """тест: форма отображает текстовое поле ввода"""

        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_)
        self.assertIn('placeholder="Enter a to-do item"', form.as_p())

    def test_validation_for_blank_items(self):
        """test: валидация формы для пустых элементов"""

        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': ''})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [EMPTY_ITEM_ERROR]
        )

    def test_form_validation_for_duplicate_text(self):
        """test: валидация формы для повторных элементов"""

        list_ = List.objects.create()
        Item.objects.create(list=list_, text="нет дубликатам!")
        form = ExistingListItemForm(for_list=list_, data={'text': 'нет дубликатам!'})
        self.assertFalse(form.is_valid())
        self.assertEqual(
            form.errors['text'],
            [DUPLICATE_ITEM_ERROR]
        )

    def test_form_save(self):
        """тест сохранения формы"""

        list_ = List.objects.create()
        form = ExistingListItemForm(for_list=list_, data={'text': 'hi'})
        new_item = form.save()
        self.assertEqual(new_item, Item.objects.all()[0])
