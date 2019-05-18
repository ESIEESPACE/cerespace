import django
from django.shortcuts import render


def index(request):
    return render(request, 'main.html')


def designer(request):
    return render(request, 'designer.html')