from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from .models import CustomUser
from profile_app.models import UserProfile  # Импорт модели профиля

# Страница регистрации
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('user_auth:login')
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    next_url = request.GET.get('next') or request.POST.get('next') or 'user_auth:home'

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect(next_url)  # редиректим на next_url (или на 'user_auth:home' если next_url пустой)
        else:
            return render(request, 'login.html', {
                'error': 'Неверный email или пароль',
                'next': next_url
            })

    return render(request, 'login.html', {'next': next_url})


# Главная страница
def home(request):
    user = request.user
    profile = None
    if user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=user)
    return render(request, 'home.html', {'user': user, 'profile': profile})
# Выход
def logout_view(request):
    logout(request)
    return redirect('user_auth:home')
