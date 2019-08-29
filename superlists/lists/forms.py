from django import forms
from django.core.exceptions import ValidationError
from django.forms.utils import ErrorList

from lists.models import Item

EMPTY_ITEM_ERROR = 'Элементы списка не должны быть пустыми'
DUPLICATE_ITEM_ERROR = 'Такой элемент уже присутствует в списке'


class ItemForm(forms.ModelForm):
    """форма для эелемента списка"""

    def save(self, for_list, commit=True):
        self.instance.list = for_list
        return super().save(commit)

    class Meta:
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control input-lg'
            })
        }
        error_messages = {
            'text': {'required': EMPTY_ITEM_ERROR}
        }


class ExistingListItemForm(forms.ModelForm):
    """форма для эелемента существующего списка"""

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None, initial=None, error_class=ErrorList,
                 label_suffix=None, empty_permitted=False, instance=None, use_required_attribute=None, for_list=None):
        super().__init__(data, files, auto_id, prefix, initial, error_class, label_suffix, empty_permitted, instance,
                         use_required_attribute)
        self.instance.list = for_list

    def validate_unique(self):
        try:
            self.instance.validate_unique()
        except ValidationError as e:
            e.error_dict = {'text': [DUPLICATE_ITEM_ERROR]}
            self._update_errors(e)

    class Meta:
        model = Item
        fields = ('text',)
        widgets = {
            'text': forms.TextInput(attrs={
                'placeholder': 'Enter a to-do item',
                'class': 'form-control input-lg'
            })
        }
        error_messages = {
            'text': {'required': EMPTY_ITEM_ERROR},
        }