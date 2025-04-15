# user_auth/urls.py
from django.urls import path
from . import views

app_name = 'user_auth'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('', views.home, name='home'),
    path('logout/', views.logout_view, name='logout')
]
