# main_project/urls.py
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('user_auth.urls')),
    path('profile/', include('profile_app.urls')),
    path('courses/',  include('courses.urls'))
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
