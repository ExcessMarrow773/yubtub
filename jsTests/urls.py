from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'jsTests'

urlpatterns = [
    path('', views.index, name='index'),
]