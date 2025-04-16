from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=100)  # имя файла курса или slug
    progress = models.FloatField(default=0.0)  # в процентах
    completed_tests = models.JSONField(default=dict)  # отслеживает какие тесты пройдены
    stars_earned = models.PositiveIntegerField(default=0)
    exp_earned = models.PositiveIntegerField(default=0)
    current_block = models.IntegerField(default=0)  # Новый блок (индекс блока в курсе)

    class Meta:
        unique_together = ('user', 'course_id')

    def __str__(self):
        return f'{self.user.email} - {self.course_id}'


