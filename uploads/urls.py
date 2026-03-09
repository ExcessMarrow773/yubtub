from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'uploads'

urlpatterns = [
	path('', views.createUpload, name='createUpload'),
	path('<int:pk>/', views.viewUpload, name='viewUpload')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)