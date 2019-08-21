from django.db import models


# Create your models here.

class Item(models.Model):
    """Элемент списка"""
    text = models.TextField(verbose_name='Текст', default='', blank=True)
