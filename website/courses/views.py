import json
import os
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.conf import settings
from .models import CourseProgress
from profile_app.models import UserProfile
from copy import deepcopy
import random

COURSES_DIR = os.path.join(settings.BASE_DIR, 'courses', 'data')

def load_course(course_id):
    try:
        with open(os.path.join(COURSES_DIR, f"{course_id}.json"), 'r', encoding='utf-8') as f:
            course_data = json.load(f)
            if 'id' not in course_data:
                raise KeyError(f"Курс {course_id} не содержит ключ 'id'")
            
            # Перемешиваем варианты ответов для заданий типа 'ordering'
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

@login_required
def course_detail(request, course_id):
    course = load_course(course_id)
    if not course:
        return HttpResponse("Курс не найден", status=404)

    sections = course.get('sections', [])

    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_id=course_id)
    section_index = progress_obj.current_section
    block_index = progress_obj.current_block

    current_section = sections[section_index]
    current_block_data = current_section['content'][block_index]
    section_completed = progress_obj.completed_blocks.get(str(section_index), [])

    incorrect = {}

    if request.method == 'POST':
        # Проверяем нажатие кнопки для ответа
        if 'submit_answer' in request.POST:
            user_answer = request.POST.getlist('answer')
            test_type = current_block_data['test_type']
            correct = current_block_data['correct']
            is_correct = False

            # Обрабатываем разные типы тестов
            if test_type in ['single_choice', 'multiple_choice']:
                is_correct = sorted(user_answer) == sorted(map(str, correct))
            elif test_type == 'ordering':
                try:
                    user_order = [int(x.strip()) for x in request.POST.get('answer', '').split(',')]
                    is_correct = user_order == correct
                except:
                    is_correct = False

            if is_correct:
                # Если ответ правильный, добавляем в прогресс
                key = str(section_index)
                if block_index not in section_completed:
                    section_completed.append(block_index)
                    progress_obj.completed_blocks[key] = section_completed
                    progress_obj.stars_earned += 10
                    progress_obj.exp_earned += 10

                    # Обновляем информацию пользователя
                    profile, created = UserProfile.objects.get_or_create(user=request.user)
                    profile.stars += 10
                    profile.exp += 10
                    profile.save()
                    progress_obj.save()

                # Автоматически переходим к следующему блоку
                if block_index + 1 < len(current_section['content']):
                    progress_obj.current_block += 1
                else:
                    progress_obj.current_section += 1
                    progress_obj.current_block = 0
                progress_obj.save()
                return redirect('courses:course_detail', course_id=course_id)

            else:
                incorrect[str(block_index)] = True

        # Обработка кнопок навигации (Назад и Вперед)
        elif 'go_back' in request.POST:
            if block_index > 0:
                progress_obj.current_block -= 1
            elif section_index > 0:
                progress_obj.current_section -= 1
                progress_obj.current_block = len(sections[section_index - 1]['content']) - 1
            progress_obj.save()
            return redirect('courses:course_detail', course_id=course_id)

        elif 'go_forward' in request.POST:
            if current_block_data['type'] == 'theory':
                if block_index + 1 < len(current_section['content']):
                    progress_obj.current_block += 1
                else:
                    progress_obj.current_section += 1
                    progress_obj.current_block = 0
                progress_obj.save()
                return redirect('courses:course_detail', course_id=course_id)

    # Вычисление общего прогресса
    total_blocks = sum(len(section['content']) for section in sections)
    completed_blocks = sum(len(v) for v in progress_obj.completed_blocks.values())
    progress_obj.progress = (completed_blocks / total_blocks) * 100
    progress_obj.save()

    # Проверка доступа к секциям и блокам
    section_locked = []
    for i, section in enumerate(sections):
        if i == 0:
            section_locked.append(False)
        else:
            prev_blocks = len(sections[i - 1]['content'])
            prev_completed = len(progress_obj.completed_blocks.get(str(i - 1), []))
            section_locked.append(prev_completed < prev_blocks)

    return render(request, 'course_detail.html', {
        'course': course,
        'sections': sections,
        'current_section_index': section_index,
        'current_block_index': block_index,
        'current_content': current_block_data,
        'can_go_back': section_index > 0 or block_index > 0,
        'can_go_forward': not section_locked[section_index] and (
            block_index + 1 < len(current_section['content']) or section_index + 1 < len(sections)
        ),
        'section_locked': section_locked,
        'completed': progress_obj.completed_blocks,
        'incorrect': incorrect,
        'progress': round(progress_obj.progress, 1),
    })

def course_list(request):
    files = os.listdir(COURSES_DIR)
    courses = []
    for filename in files:
        if filename.endswith('.json'):
            data = load_course(filename[:-5])
            progress = 0  # По умолчанию прогресс 0, если пользователь не залогинен
            if request.user.is_authenticated:
                try:
                    progress = CourseProgress.objects.get(user=request.user, course_id=data["id"]).progress
                except CourseProgress.DoesNotExist:
                    progress = 0
            data['progress'] = round(progress, 1)
            courses.append(data)
    return render(request, 'course_list.html', {'courses': courses})
