from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import PhotoUploadForm
from .models import UserProfile
from courses.models import CourseProgress
from django.contrib.auth import logout
from django.http import HttpResponseForbidden

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

    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_app:profile')
    else:
        form = PhotoUploadForm(instance=profile)

    course_progress_list = []
    for progress in CourseProgress.objects.filter(user=request.user):
        course_meta = load_course_metadata(progress.course_id)
        course_progress_list.append({
            'title': course_meta['title'],
            'photo': course_meta['photo'],  # это имя файла типа "mycourse.jpg"
            'completed_percent': round(progress.progress, 1),
        })

    return render(request, 'profile.html', {
        'profile': profile,
        'form': form,
        'course_progress_list': course_progress_list,
    })

@login_required
def delete_profile(request):
    if request.method == "POST":
        user = request.user
        user.profile.delete()  # Удалить профиль
        user.delete()  # Удалить самого пользователя
        logout(request)  # Выход из системы
        return redirect('home')  # Перенаправить на главную страницу
    else:
        return HttpResponseForbidden("Неверный запрос")

