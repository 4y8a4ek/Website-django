from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'courses'

urlpatterns = [
    path('', views.course_list, name='course_list'),
    path('<str:course_id>/', views.course_detail, name='course_detail'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT);
