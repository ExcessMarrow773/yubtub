from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('signup/', views.register, name='register'),
    path('video/', views.postVideo, name='postVideo'),
    path('watch/<int:pk>', views.watchVideo, name='watch')
 ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)