from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # обязательно!
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class UserRole(models.TextChoices):
    DEAN = 'dean', 'Деканат факультета'
    HEADMAN = 'headman', 'Староста группы'
    STUDENT = 'student', 'Студент'
    GUEST = 'guest', 'Не являюсь студентом'

class StudyGroup(models.TextChoices):
    NONE = 'non', 'Не являюсь студентом'
    CS_101 = 'cs101', 'CS-101'
    CS_102 = 'cs102', 'CS-102'
    MATH_201 = 'math201', 'MATH-201'

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    surname = models.CharField(max_length=255)
    
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.STUDENT
    )

    group = models.CharField(
        max_length=20,
        choices=StudyGroup.choices,
        default=StudyGroup.NONE
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    @property
    def full_name(self):
        return f"{self.name} {self.surname}"
    def __str__(self):
        return self.email

