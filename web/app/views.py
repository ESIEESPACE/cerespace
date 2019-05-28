import datetime
import os

import django
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from cerespace_web.settings import MEDIA_ROOT


def index(request: django.http.HttpRequest):
    return render(request, 'main.html')


def designer(request: django.http.HttpRequest):
    return render(request, 'designer.html')


def control(request: django.http.HttpRequest):
    return render(request, 'control.html')


@csrf_exempt
def photo_upload(request: django.http.HttpRequest):
    if request.method == "POST" and request.FILES["photo"]:
        photo = request.FILES['photo']
        fs = FileSystemStorage()
        filename = os.path.join(MEDIA_ROOT, datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S.png"))
        print(filename)
        fs.save(filename, photo)
        return redirect("/")

    elif request.method == "GET":
        raise Http404()

    return redirect("/")
