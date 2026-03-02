from django.contrib import admin
from django.urls import path
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from .models import UserRole, StudyGroup
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser

    list_display = ('email', 'name', 'role', 'group', 'is_staff', 'is_active')
    list_filter = ('role', 'group', 'is_staff', 'is_active')

    ordering = ('email',)
    search_fields = ('email', 'name')

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        ('Персональная информация', {
            'fields': ('name', 'role', 'group')
        }),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Даты', {
            'fields': ('last_login',)
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'role', 'group', 'password1', 'password2', 'is_staff', 'is_superuser'),
        }),
    )

    readonly_fields = ('last_login',)
    
urlpatterns = [
    path('admin/', admin.site.urls),
]