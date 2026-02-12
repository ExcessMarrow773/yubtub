from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'accounts'

urlpatterns = [
    path('', views.settings, name='settings'),
    path('changeUsername/', views.settings, name='changeUsername'),
    path('changePassword/', views.settings, name='changePassword'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)