from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .decorators import profile_required
from .forms import RegistrationForm
from .models import *
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
        role = request.POST.get('role') or UserRole.STUDENT
        group = request.POST.get('group') or StudyGroup.NONE

        if CustomUser.objects.filter(email=email).exists():
            return render(request, 'register.html', {'error': 'Email уже зарегистрирован'})

        if role == 'guest':
            group = 'none'

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            name=name,
            role=role,
            group=group
        )

        UserProfile.objects.create(user=user)

        user = authenticate(request, email=email, password=password)
        if user:
            login(request, user)
            return redirect('user_auth:profile_fill')

    return render(request, 'register.html', {
        'roles': UserRole.choices,
        'groups': StudyGroup.choices,
    })



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


@profile_required
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

@login_required
@profile_required
def progress_panel(request):
    user = request.user

    if user.role not in [UserRole.DEAN, UserRole.HEADMAN]:
        return redirect('user_auth:home')

    selected_group = None
    selected_course = request.GET.get('course')
    sort = request.GET.get('sort', 'user')

    # 👑 деканат
    if user.role == UserRole.DEAN:
        selected_group = request.GET.get('group')

    # ⭐ староста
    if user.role == UserRole.HEADMAN:
        selected_group = user.group

    users = CustomUser.objects.filter(group=selected_group)

    progress = CourseProgress.objects.filter(user__in=users)

    if selected_course:
        progress = progress.filter(course_id=selected_course)

    # сортировка
    if sort == 'progress':
        progress = progress.order_by('-progress')
    else:
        progress = progress.order_by('user__name')

    # список курсов (уникальные)
    courses = (
        CourseProgress.objects
        .values_list('course_id', flat=True)
        .distinct()
    )

    return render(request, 'progress_panel.html', {
        'progress': progress.select_related('user'),
        'groups': StudyGroup.choices if user.role == UserRole.DEAN else None,
        'selected_group': selected_group,
        'courses': courses,
        'selected_course': selected_course,
        'sort': sort,
        'is_dean': user.role == UserRole.DEAN,
    })


@login_required
def manage_users(request):
    if request.user.role != UserRole.DEAN:
        return redirect('user_auth:home')

    selected_group = request.GET.get('group')

    users = CustomUser.objects.exclude(role=UserRole.DEAN)

    if selected_group:
        users = users.filter(group=selected_group)

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        role = request.POST.get('role')
        group = request.POST.get('group')

        user = CustomUser.objects.get(id=user_id)

        if role == UserRole.GUEST:
            group = StudyGroup.NONE

        user.role = role
        user.group = group
        user.save()

        return redirect('user_auth:manage_users')

    return render(request, 'manage_users.html', {
        'users': users,
        'roles': UserRole.choices,
        'groups': StudyGroup.choices,
        'selected_group': selected_group,
    })


from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from profile_app.forms import ProfileForm

@login_required
def profile_fill(request):
    profile = request.user.userprofile
    if profile.is_complete():
        # если анкета уже заполнена — редирект на главную
        return redirect('user_auth:home')

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_auth:home')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profile_fill.html', {'form': form})