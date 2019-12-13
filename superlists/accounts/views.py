from django.contrib import messages, auth
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.urls import reverse

from accounts.models import Token


def send_login_email(request):
    """отправка ссылки для входа на email"""

    email = request.POST['email']
    token = Token.objects.create(email=email)
    url = request.build_absolute_uri(
        reverse('login') + '?token=' + str(token.uid)
    )
    send_mail(
        'Ссылка для входа на сайт списков',
        f'Чтобы войти на сайт перейдите по ссылке: \n{url}',
        'al-fa-y@yandex.ru',
        [email]
    )
    messages.success(request, 'На вашу почту отправлена ссылка')

    return redirect('/')


def login(request):
    """вход пользователя по ссылке"""

    token = request.GET.get('token')
    user = auth.authenticate(uid=token)
    if user:
        auth.login(request, user)
    return redirect('/')
