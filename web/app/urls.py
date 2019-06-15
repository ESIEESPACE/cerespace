from django.conf.urls import url
from django.conf.urls.static import static
from django.urls import path

from cerespace_web import settings
from . import views

urlpatterns = [
                  path('', views.index, name="index"),
                  path('designer', views.designer, name="designer"),
                  path('controller', views.control, name="controller"),
                  path('photo_upload', views.photo_upload, name="photo_upload"),
                  path('settings', views.settings, name="settings"),
              ] + static(settings.STATIC_URL)
