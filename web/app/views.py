import datetime
import os

import django
from django.core.files.storage import FileSystemStorage
from django.http import HttpRequest, Http404, HttpResponse, HttpResponseServerError
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from cerespace_web.settings import MEDIA_ROOT


def index(request: django.http.HttpRequest):
    return render(request, 'main.html')


def designer(request: django.http.HttpRequest):
    return render(request, 'designer.html')


def control(request: django.http.HttpRequest):
    return render(request, 'control.html')


def settings(request: django.http.HttpRequest):
    return render(request, 'settings.html')


def event(request: django.http.HttpRequest):
    return render(request, 'event.html')


@csrf_exempt
def photo_upload(request: django.http.HttpRequest):
    if request.method == "POST" and request.FILES["photo"]:
        photo = request.FILES['photo']
        fs = FileSystemStorage()
        filename = datetime.datetime.now().strftime("%Y_%m_%d_%H%M%S.png")
        complete_filename = os.path.join(MEDIA_ROOT + "/upload", filename)
        fs.save(complete_filename, photo)
        return HttpResponse(filename)

    elif request.method == "POST":
        return HttpResponseServerError()

    elif request.method == "GET":
        raise Http404()
