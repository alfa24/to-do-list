from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.
from lists.models import Item


def home_page(request):
    """домашняя страница"""
    if request.method == 'POST':
        new_item_text = request.POST.get('item_text', '')
        Item.objects.create(text=new_item_text)
    else:
        new_item_text = ''

    return render(request, 'home.html',
                  {'new_item_text': new_item_text}
                  )
