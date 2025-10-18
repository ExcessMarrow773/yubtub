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
    path('watch/<int:pk>', views.watchVideo, name='watch'),
    path('account/<str:username>/', views.account, name='account'),
    path('like-video/', views.like_video, name="like-video"),
    path('TODO/', views.TODO, name='TODO'),
    path('cornhub/', views.cornhub, name='cornhub'),
    path('makePost/', views.makePost, name='makePost'),
    path('posts/', views.postIndex, name="postIndex"),
    path('post/<int:pk>/', views.viewPost, name='post'),
    path('mdHelp/', views.mdHelp, name='mdHelp'),
    path('follow-user/', views.follow_user, name="follow-user"),
    path('following/', views.following, name="following"),
 ]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)