from django import forms

from lists.models import Item

EMPTY_ITEM_ERROR = 'Элементы списка не должны быть пустыми'


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