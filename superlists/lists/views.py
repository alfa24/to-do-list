from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from lists.models import Item


def home_page(request):
    """домашняя страница"""
    if request.method == 'POST':
        Item.objects.create(text=request.POST['item_text'])
        return redirect('/lists/edith/')

    return render(request, 'home.html')


def view_list(request):
    """представление списка"""
    items = Item.objects.all()
    return render(request, 'list.html', {'items': items})
