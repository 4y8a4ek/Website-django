from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .forms import RegistrationForm
from .models import CustomUser

# Страница регистрации
def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return redirect('user_auth:login')  # Перенаправление на страницу входа
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

# Страница входа
def login_view(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_auth:home')  # или другой маршрут
        else:
            return render(request, 'login.html', {'error': 'Неверный email или пароль'})
    return render(request, 'login.html')

def home(request):
    return render(request, 'home.html')

def logout_view(request):
    logout(request)
    return redirect('user_auth:home')