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
from django.contrib import messages

COURSES_DIR = os.path.join(settings.BASE_DIR, 'courses', 'data')
import re


def highlight_code_blocks(text):
    # Ищем 'code' с пробелами и содержимое до следующего 'code' с пробелами
    pattern = r"'code'\s*( .*?) \s*'code'"
    
    def repl(m):
        code_text = m.group(1)
        # Заменим литералы \n на переносы, если надо
        code_text = code_text.replace('\\n', '\n')
        return f'<pre><code class="language-python">{code_text}</code></pre>'
    
    return re.sub(pattern, repl, text, flags=re.DOTALL)




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

@login_required
def course_detail(request, course_id):
    course = load_course(course_id)
    if not course:
        return HttpResponse("Курс не найден", status=404)

    sections = course.get('sections', [])
    blocks_flat = [block for section in sections for block in section['content']]
    total_blocks = len(blocks_flat)

    progress_obj, _ = CourseProgress.objects.get_or_create(user=request.user, course_id=course_id)
    block_index = progress_obj.current_block

    if block_index >= total_blocks:
        block_index = total_blocks - 1
        progress_obj.current_block = block_index
        progress_obj.save()

    current_block_data = blocks_flat[block_index]
    block_global_id = current_block_data.get('id')
    is_theory = current_block_data.get('type') == 'theory'

    # Проверка ошибок
    incorrect = {}
    session_incorrect = request.session.pop('incorrect', None)
    if session_incorrect:
        incorrect.update(session_incorrect)
    if 'question' in current_block_data:
        current_block_data['question'] = highlight_code_blocks(current_block_data['question'])
    # POST-обработка
    if request.method == 'POST':
        if 'submit_answer' in request.POST:
            user_answer = request.POST.getlist('answer')
            test_type = current_block_data.get('test_type')
            correct = current_block_data.get('correct', [])
            is_correct = False

            if test_type in ['single_choice', 'multiple_choice']:
                is_correct = sorted(user_answer) == sorted(map(str, correct))
            elif test_type == 'ordering':
                try:
                    user_order = [int(x.strip()) for x in request.POST.get('answer', '').split(',')]
                    is_correct = user_order == correct
                except Exception:
                    is_correct = False
            elif test_type == 'text_input':
                is_correct = user_answer == [correct]
            elif test_type == 'fill_in_the_blanks':
                user_inputs = [request.POST.get(f'answer{i}', '') for i in range(len(correct))]
                is_correct = user_inputs == correct
            elif test_type == 'matching':
                selected_matches = [request.POST.get(f'match_{i}') for i in range(len(correct))]
                is_correct = selected_matches == correct
            elif test_type == 'open_answer':
                is_correct = True  # Всегда "верно"

            if is_correct:
                # Обновляем только если блок ещё не засчитан
                if block_index >= progress_obj.completed_blocks:
                    progress_obj.completed_blocks += 1
                    progress_obj.progress = (progress_obj.completed_blocks / total_blocks) * 100
                profile, _ = UserProfile.objects.get_or_create(user=request.user)
                profile.exp += 50  # Например, добавляем 10 exp
                profile.stars += 10  # Например, даём 1 звезду
                profile.save()
                
            else:
                incorrect[str(block_index)] = True
                request.session['incorrect'] = incorrect
                messages.error(request, "error")

            progress_obj.save()
            if 'question' in current_block_data:
                current_block_data['question'] = highlight_code_blocks(current_block_data['question'])
            return redirect('courses:course_detail', course_id=course_id)
        
        elif 'jump_to_section' in request.POST:
                section_idx = int(request.POST['jump_to_section'])
                target_section = sections[section_idx]
                # Перейти к первому блоку секции
                target_block_index = sum(len(s['content']) for s in sections[:section_idx])
                progress_obj.current_block = target_block_index
                progress_obj.save()
                if 'question' in current_block_data:
                    current_block_data['question'] = highlight_code_blocks(current_block_data['question'])
                return redirect('courses:course_detail', course_id=course_id)

        elif 'go_back' in request.POST:
            if block_index > 0:
                progress_obj.current_block -= 1
                progress_obj.save()
            if 'question' in current_block_data:
                current_block_data['question'] = highlight_code_blocks(current_block_data['question'])
            return redirect('courses:course_detail', course_id=course_id)

        elif 'go_forward' in request.POST:
            if block_index + 1 < total_blocks:
                progress_obj.current_block += 1
                progress_obj.save()
            if 'question' in current_block_data:
                current_block_data['question'] = highlight_code_blocks(current_block_data['question'])
            return redirect('courses:course_detail', course_id=course_id)

    # Теория автоматически считается пройденной
    if is_theory and block_index >= progress_obj.completed_blocks:
        progress_obj.completed_blocks += 1
        progress_obj.progress = (progress_obj.completed_blocks / total_blocks) * 100
        progress_obj.save()

    # Определяем, какие секции заблокированы
    completed = int(progress_obj.completed_blocks)  # Преобразуем в целое число
    section_locked = []
    blocks_seen = 0
    for section in sections:
        section_block_count = len(section['content'])
        # Преобразуем в целое число перед сравнением
        section_locked.append(blocks_seen >= completed)
        blocks_seen += section_block_count  # увеличиваем количество пройденных блоков

    # Определение текущего блока по секции и индексу
    cur_section_idx, cur_block_idx = 0, 0
    remaining = block_index  # копия block_index

    for i, section in enumerate(sections):
        section_length = len(section['content'])
        if remaining < section_length:
            cur_section_idx = i
            break
    profile = None
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if 'question' in current_block_data:
        current_block_data['question'] = highlight_code_blocks(current_block_data['question'])
    if 'text' in current_block_data:
        current_block_data['text'] = highlight_code_blocks(current_block_data['text'])
    return render(request, 'course_detail.html', {
        'course': course,
        'sections': sections,
        'current_section_index': cur_section_idx,
        'current_block_index': block_index,
        'current_content': current_block_data,
        'can_go_back': block_index > 0,
        'can_go_forward': block_index + 1 < total_blocks and block_index < progress_obj.completed_blocks,
        'section_locked': section_locked,
        'completed': completed - 1,
        'incorrect': incorrect,
        'progress': round(progress_obj.progress, 1),
        'profile': profile,
    })



def course_list(request):
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
        

    # Группировка по полю group (только для "все курсы")
    grouped_all = {}
    for course in all_courses:
        group = course.get('group', 'Без группы')
        grouped_all.setdefault(group, []).append(course)

    profile = None
    if request.user.is_authenticated:
        profile, _ = UserProfile.objects.get_or_create(user=request.user)

    return render(request, 'course_list.html', {
        'grouped_all': grouped_all,
        'active_courses': active_courses,
        'completed_courses': completed_courses,
        'profile': profile
    })
