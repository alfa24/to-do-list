from django.http import HttpResponse
from django.shortcuts import render


# Create your views here.


def home_page(request):
    """домашняя страница"""
    return HttpResponse('<html><title>To-DO lists</title></html>')
