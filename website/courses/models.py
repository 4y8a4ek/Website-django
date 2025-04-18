from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=100)
    progress = models.FloatField(default=0.0)
    completed_tests = models.JSONField(default=dict)
    completed_blocks = models.JSONField(default=dict)  # ключ: секция, значение: список пройденных индексов блоков
    stars_earned = models.PositiveIntegerField(default=0)
    exp_earned = models.PositiveIntegerField(default=0)
    current_section = models.IntegerField(default=0)
    current_block = models.IntegerField(default=0)

    class Meta:
        unique_together = ('user', 'course_id')

    def __str__(self):
        return f'{self.user.email} - {self.course_id}'
