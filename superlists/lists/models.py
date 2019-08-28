from django.db import models

# Create your models here.
from django.urls import reverse


class List(models.Model):
    """модель списка"""

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])


class Item(models.Model):
    """Элемент списка"""
    text = models.TextField(verbose_name='Текст')
    list = models.ForeignKey(List, default=None)
