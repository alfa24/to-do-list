from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from lists.models import Item, List


# todo удалить хардкод в url

def home_page(request):
    """домашняя страница"""

    return render(request, 'home.html')


def view_list(request, list_id):
    """представление списка"""
    list_ = List.objects.get(id=list_id)
    return render(request, 'list.html', {'list': list_})


def new_list(request):
    list_ = List.objects.create()
    item = Item(text=request.POST['item_text'], list=list_)

    try:
        item.full_clean()
        item.save()
    except ValidationError as e:
        list_.delete()
        error = 'Элементы списка не должны быть пустыми'
        return render(request, 'home.html', {'error': error})

    return redirect(f'/lists/{list_.id}/')


def add_item(request, list_id):
    """добавление новой записи"""
    list_ = List.objects.get(id=list_id)
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect(f'/lists/{list_.id}/')
