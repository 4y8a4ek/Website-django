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

    try:
        progress_obj = CourseProgress.objects.get(user=request.user, course_id=course_id)
    except CourseProgress.DoesNotExist:
        progress_obj = CourseProgress.objects.create(user=request.user, course_id=course_id)

    current_block = progress_obj.current_block
    incorrect = {}
    correct_answers = {}

    if request.method == 'POST':
        if 'go_back' in request.POST and current_block > 0:
            progress_obj.current_block -= 1
            progress_obj.save()
            return redirect('courses:course_detail', course_id=course_id)

        if 'go_forward' in request.POST and current_block < len(course['content']) - 1:
            current_content = course['content'][current_block]
            if current_content['type'] == 'theory' or progress_obj.completed_tests.get(str(current_block)):
                progress_obj.current_block += 1
                progress_obj.save()
                return redirect('courses:course_detail', course_id=course_id)

        current_content = course['content'][current_block]
        if current_content['type'] == 'test':
            index = current_block
            user_answer = request.POST.getlist('answer')
            correct = current_content['correct']
            test_type = current_content['test_type']
            is_correct = False

            if test_type in ['single_choice', 'multiple_choice']:
                is_correct = sorted(user_answer) == sorted(map(str, correct))
                correct_answers[str(index)] = correct
            elif test_type == 'ordering':
                try:
                    user_order = [int(x.strip()) for x in request.POST.get('answer', '').split(',')]
                    is_correct = user_order == correct
                    correct_answers[str(index)] = correct
                except:
                    is_correct = False

            if is_correct:
                if not progress_obj.completed_tests.get(str(index)):
                    progress_obj.completed_tests[str(index)] = True
                    progress_obj.stars_earned += 10
                    progress_obj.exp_earned += course['exp'] // len(course['content'])
                    profile, _ = UserProfile.objects.get_or_create(user=request.user)
                    profile.exp += course['exp'] // len(course['content'])
                    profile.stars += 10
                    profile.save()
                if not progress_obj.completed_tests.get(str(index)):
                    progress_obj.completed_tests[str(index)] = True
                    progress_obj.stars_earned += current_content.get('stars', 1)
                    progress_obj.exp_earned += course['exp'] // len(course['content'])

                    profile, _ = UserProfile.objects.get_or_create(user=request.user)
                    profile.exp += course['exp'] // len(course['content'])
                    profile.stars += current_content.get('stars', 1)
                    profile.save()

                progress_obj.save()
            else:
                incorrect[str(index)] = True
                correct_answers[str(index)] = correct

    progress = progress_obj.progress
    completed = progress_obj.completed_tests
    current_content = course['content'][current_block]

    # Показываем правильные ответы, если тест уже пройден
    if current_content['type'] == 'test':
        index = current_block
        if progress_obj.completed_tests.get(str(index)):
            correct_answers[str(index)] = current_content['correct']

    return render(request, 'course_detail.html', {
        'course': course,
        'progress': progress,
        'completed': completed,
        'incorrect': incorrect,
        'correct_answers': correct_answers,
        'current_content': current_content,
        'current_block': current_block,
        'can_go_back': current_block > 0,
        'can_go_forward': current_block < len(course['content']) - 1,
    })

@login_required
def course_list(request):
    files = os.listdir(COURSES_DIR)
    courses = []
    for filename in files:
        if filename.endswith('.json'):
            data = load_course(filename[:-5])
            try:
                progress = CourseProgress.objects.get(user=request.user, course_id=data["id"]).progress
            except CourseProgress.DoesNotExist:
                progress = 0
            data['progress'] = round(progress, 1)
            courses.append(data)
    return render(request, 'course_list.html', {'courses': courses})
