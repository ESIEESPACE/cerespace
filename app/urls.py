from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

from cerespace_web import settings
from . import views


urlpatterns = [
    path('', views.index, name="index")
] + static(settings.STATIC_URL)