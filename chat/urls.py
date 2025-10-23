from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.index, name='index'),
    path('<str:account>', views.chat, name='chat'),
 ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)