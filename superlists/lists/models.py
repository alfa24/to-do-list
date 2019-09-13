from django.conf import settings
from django.db import models

# Create your models here.
from django.urls import reverse


class List(models.Model):
    """модель списка"""

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    @property
    def name(self):
        """имя"""

        return self.item_set.first().text

    def get_absolute_url(self):
        return reverse('view_list', args=[self.id])


class Item(models.Model):
    """Элемент списка"""
    text = models.TextField(verbose_name='Текст', default='')
    list = models.ForeignKey(List, default=None)

    def __str__(self):
        return self.text

    class Meta:
        ordering = ('id',)
        unique_together = ('text', 'list')
