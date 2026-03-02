from django import forms
from .models import UserProfile

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo']


class ProfileForm(forms.ModelForm):
    LEARNING_FORMATS = [
        ('video', 'Видео-уроки'),
        ('text', 'Текстовые материалы'),
        ('practice', 'Практические задания'),
        ('online', 'Онлайн-курсы и вебинары'),
    ]
    MOTIVATIONS = [
        ('hobby', 'Для хобби и интереса'),
        ('career', 'Для будущей работы и карьеры'),
        ('study', 'Для учебы и улучшения знаний'),
        ('projects', 'Для личных проектов и экспериментов'),
    ]
    DIFFICULTIES = [
        ('hard_material', 'Сложный материал'),
        ('time', 'Мало времени на обучение'),
        ('practice', 'Недостаточно практики'),
        ('motivation', 'Сложно поддерживать мотивацию'),
    ]

    preferred_learning_formats = forms.MultipleChoiceField(
        choices=LEARNING_FORMATS,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Какие форматы обучения вам нравятся?"
    )
    motivation = forms.MultipleChoiceField(
        choices=MOTIVATIONS,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Что вас мотивирует изучать?"
    )
    learning_difficulties = forms.MultipleChoiceField(
        choices=DIFFICULTIES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="С какими трудностями вы сталкиваетесь?"
    )

    class Meta:
        model = UserProfile
        fields = [
            'interest_programming',
            'interest_math',
            'weekly_learning_time',
            'preferred_learning_formats',
            'motivation',
            'learning_difficulties'
        ]
        labels = {
            'interest_programming': 'Как вы оцениваете свой интерес к программированию?',
            'interest_math': 'Как вы оцениваете свой интерес к математике?',
            'weekly_learning_time': 'Сколько времени вы уделяете обучению в неделю?'
        }