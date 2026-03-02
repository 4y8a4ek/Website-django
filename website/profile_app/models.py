from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    exp = models.IntegerField(default=0)
    stars = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='profile_photos/', default='profile_photos/default.png')
    
    # поля анкеты
    birth_date = models.DateField(null=True, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)

    def is_complete(self):
        """Проверка, заполнена ли анкета"""
        return bool(self.birth_date and self.phone and self.city)

    def __str__(self):
        return self.user.email