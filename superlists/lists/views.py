from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from lists.forms import ItemForm, ExistingListItemForm, NewListForm
from lists.models import Item, List

User = get_user_model()


def home_page(request):
    """домашняя страница"""

    return render(request, 'home.html', {'form': ItemForm()})


def view_list(request, list_id):
    """представление списка"""
    list_ = List.objects.get(id=list_id)
    form = ExistingListItemForm(for_list=list_)
    if request.method == 'POST':
        form = ExistingListItemForm(for_list=list_, data=request.POST)
        if form.is_valid():
            form.save()
            return redirect(list_)

    return render(request, 'list.html', {'list': list_, 'form': form})


def new_list(request):
    """новый список 2"""

    form = NewListForm(data=request.POST)

    if form.is_valid():
        list_ = form.save(owner=request.user)
        return redirect(list_)

    return render(request, 'home.html', {'form': form})


def my_lists(request, email):
    """мои списки"""

    owner = User.objects.get(email=email)
    return render(request, 'my_lists.html', {'owner': owner})


def share_list(request, list_id):
    """поделиться списком"""
    email = request.POST.get('sharee')
    list_ = List.objects.get(id=list_id)
    user = User.objects.filter(email=email).first()
    print(email, user, list_)
    if user:
        list_.shared_with.add(user)
    return redirect(list_)
