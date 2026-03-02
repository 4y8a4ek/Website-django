from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    exp = models.IntegerField(default=0)
    stars = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='profile_photos/', default='profile_photos/default.png')
    
    # Вопросы анкеты
    interest_programming = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Низкий'),
            ('medium', 'Средний'),
            ('high', 'Высокий')
        ],
        verbose_name="Как вы оцениваете свой интерес к программированию?",
        blank=True
    )
    interest_math = models.CharField(
        max_length=20,
        choices=[
            ('low', 'Низкий'),
            ('medium', 'Средний'),
            ('high', 'Высокий')
        ],
        verbose_name="Как вы оцениваете свой интерес к математике?",
        blank=True
    )
    weekly_learning_time = models.CharField(
        max_length=20,
        choices=[
            ('<1', 'Меньше 1 часа в неделю'),
            ('1-3', '1–3 часа в неделю'),
            ('3-5', '3–5 часов в неделю'),
            ('>5', 'Более 5 часов в неделю')
        ],
        verbose_name="Сколько времени вы обычно посвящаете обучению в неделю?",
        blank=True
    )
    preferred_learning_formats = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Какие форматы обучения вам больше нравятся?"
    )
    motivation = models.JSONField(
        default=list,
        blank=True,
        verbose_name="Что вас мотивирует изучать программирование и математику?"
    )
    learning_difficulties = models.JSONField(
        default=list,
        blank=True,
        verbose_name="С какими трудностями вы сталкиваетесь при обучении?"
    )

    def is_complete(self):
        """Проверка, заполнена ли анкета"""
        basic_filled = bool(
            self.interest_programming and
            self.interest_math and
            self.weekly_learning_time
        )
        return basic_filled

    def __str__(self):
        return self.user.email