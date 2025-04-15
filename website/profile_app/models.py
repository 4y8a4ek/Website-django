from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    exp = models.IntegerField(default=0)
    stars = models.IntegerField(default=0)
    photo = models.ImageField(upload_to='profile_photos/', default='profile_photos/default.png')

    def __str__(self):
        return self.user.email
