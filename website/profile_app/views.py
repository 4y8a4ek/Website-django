from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PhotoUploadForm
from .models import UserProfile
from courses.models import CourseProgress
from django.contrib.auth import logout
from django.http import HttpResponseForbidden
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
import os
import json
from django.conf import settings
from courses.models import CourseProgress

def load_course_metadata(course_id):
    path = os.path.join(settings.BASE_DIR, 'courses', 'data', f'{course_id}.json')
    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return {
                'title': data.get('title', 'Без названия'),
                'photo': data.get('photo', None)
            }
    except FileNotFoundError:
        return {
            'title': course_id,
            'photo': None
        }

@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    photo_form = PhotoUploadForm(request.POST or None, request.FILES or None, instance=profile)

    name_updated = False
    email_updated = False
    password_updated = False

    if request.method == 'POST':
        # Обработка обновления фото
        if 'update_photo' in request.POST and photo_form.is_valid():
            photo_form.save()
            return redirect('profile_app:profile')

        # Обработка изменения имени
        if 'change_name' in request.POST:
            new_name = request.POST.get('new_name', '').strip()
            if new_name and new_name != request.user.name:
                request.user.name = new_name
                request.user.save()
                name_updated = True
            print("POST data:", request.POST)


        # Обработка изменения email
        if 'change_email' in request.POST:
            new_email = request.POST.get('new_email', '').strip()
            if new_email and new_email != request.user.email:
                request.user.email = new_email
                request.user.save()
                email_updated = True

        # Обработка смены пароля
        if 'change_password' in request.POST:
            current_password = request.POST.get('current_password')
            new_password = request.POST.get('new_password')
            # Проверяем правильность текущего пароля
            if not request.user.check_password(current_password):
                messages.error(request, 'Текущий пароль неверен.')
                return redirect('profile_app:profile')

            # Обновляем пароль
            request.user.set_password(new_password)
            request.user.save()

            # Обновляем сессию для нового пароля
            update_session_auth_hash(request, request.user)

            messages.success(request, 'Пароль успешно обновлён.')
            return redirect('profile_app:profile')

        # Обработка удаления профиля
        if 'delete_profile' in request.POST:
            request.user.delete()
            return redirect('user_auth:home')  # или куда нужно

    # Получаем все прогрессы пользователя
    course_progress_list = []
    completed_courses = []
    active_courses = []
    for progress in CourseProgress.objects.filter(user=request.user):
        course_meta = load_course_metadata(progress.course_id)
        course_data = {
            'title': course_meta['title'],
            'photo': course_meta['photo'],
        }

        if progress.progress == 100:
            completed_courses.append(course_data)
        else:
            course_data['completed_percent'] = round(progress.progress, 1)
            active_courses.append(course_data)

    return render(request, 'profile.html', {
        'profile': profile,
        'photo_form': photo_form,
        'completed_courses': completed_courses,
        'active_courses': active_courses,
        'name_updated': name_updated,
        'email_updated': email_updated,
        'password_updated': password_updated,
    })



@login_required
def delete_profile(request):
    if request.method == "POST":
        user = request.user

        # Удаляем связанные объекты
        UserProfile.objects.filter(user=user).delete()
        CourseProgress.objects.filter(user=user).delete()

        # Удаляем самого пользователя
        user.delete()

        # Завершаем сессию
        logout(request)

        return redirect('auth_user:home')
    else:
        return HttpResponseForbidden("Неверный запрос")

