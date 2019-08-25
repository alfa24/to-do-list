from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from lists.models import Item, List


def home_page(request):
    """домашняя страница"""

    return render(request, 'home.html')


def view_list(request):
    """представление списка"""
    items = Item.objects.all()
    return render(request, 'list.html', {'items': items})


def new_list(request):
    list_ = List.objects.create()
    Item.objects.create(text=request.POST['item_text'], list=list_)
    return redirect('/lists/edith/')
