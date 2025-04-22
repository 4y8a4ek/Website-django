from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class CourseProgress(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=100)
    progress = models.FloatField(default=0.0)
    completed_blocks = models.PositiveIntegerField(default=0)  # Количество завершённых блоков
    current_block = models.IntegerField(default=0)  # Индекс текущего блока (глобальный)

    class Meta:
        unique_together = ('user', 'course_id')

    def __str__(self):
        return f'{self.user.email} - {self.course_id}'

