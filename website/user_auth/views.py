from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from .models import CustomUser
from profile_app.models import UserProfile  # Импорт модели профиля
import json
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from courses.models import CourseProgress
from profile_app.models import UserProfile
from copy import deepcopy
import random
from django.contrib import messages
COURSES_DIR = os.path.join(settings.BASE_DIR, 'courses', 'data')
# Страница регистрации
def load_course(course_id):
    try:
        with open(os.path.join(COURSES_DIR, f"{course_id}.json"), 'r', encoding='utf-8') as f:
            course_data = json.load(f)
            if 'id' not in course_data:
                raise KeyError(f"Курс {course_id} не содержит ключ 'id'")
            for test in course_data.get('content', []):
                if test['type'] == 'test' and test.get('test_type') == 'ordering':
                    original = test['options']
                    shuffled = deepcopy(original)
                    random.shuffle(shuffled)
                    test['shuffled_options'] = shuffled
                    test['shuffled_to_correct'] = [original.index(opt) for opt in shuffled]
            return course_data
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    
def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password1')

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email уже зарегистрирован'})

        user = CustomUser.objects.create_user(email=email, password=password, name=name)
        UserProfile.objects.create(user=user)

        # Используем authenticate — он сам определит backend
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)  # Теперь backend установлен правильно
            return redirect('user_auth:home')
        else:
            return render(request, 'register.html', {'error': 'Ошибка входа после регистрации'})

    return render(request, 'register.html')


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
    files = os.listdir(COURSES_DIR)
    all_courses = []
    active_courses = []
    completed_courses = []

    for filename in files:
        if filename.endswith('.json'):
            data = load_course(filename[:-5])
            progress = 0
            if request.user.is_authenticated:
                try:
                    progress = CourseProgress.objects.get(user=request.user, course_id=data["id"]).progress
                except CourseProgress.DoesNotExist:
                    progress = 0
            data['progress'] = round(progress, 1)

            all_courses.append(data)
            if data['progress'] >= 100:
                completed_courses.append(data)
            if data['progress'] != 100 and data['progress'] != 0:
                active_courses.append(data)
    grouped_all = {}
    for course in all_courses:
        group = course.get('group', 'Без группы')
        grouped_all.setdefault(group, []).append(course)
    if user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(user=user)
    return render(request, 'home.html', {'user': user, 'profile': profile, 'grouped_all': grouped_all,})
# Выход
def logout_view(request):
    logout(request)
    return redirect('user_auth:home')
