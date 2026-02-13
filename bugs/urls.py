from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'bugs'

urlpatterns = [
    path('', views.bug_report, name='bugReport'),
    path('reports/', views.bug_reportIndex, name="bugReportIndex"),
    path('view/<int:pk>', views.bugView, name="bugView"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)