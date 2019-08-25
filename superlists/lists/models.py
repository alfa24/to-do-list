from django.db import models


# Create your models here.

class List(models.Model):
    """Название списка"""
    pass


class Item(models.Model):
    """Элемент списка"""
    text = models.TextField(verbose_name='Текст', default='', blank=True)
    list = models.ForeignKey(List, default=None)
