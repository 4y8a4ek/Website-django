from django.urls import path
from .views import profile_view, delete_profile
from django.conf import settings
from django.conf.urls.static import static

app_name = 'profile_app'

urlpatterns = [
    path('', profile_view, name='profile'),
    path('delete_profile/', delete_profile , name='delete_profile')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
