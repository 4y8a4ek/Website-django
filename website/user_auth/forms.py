from django import forms
from .models import *

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['name', 'email', 'password', 'role', 'group']

    def clean(self):
        cleaned = super().clean()
        role = cleaned.get('role')
        group = cleaned.get('group')

        # если не студент — группа должна быть NONE
        if role == UserRole.GUEST:
            cleaned['group'] = StudyGroup.NONE

        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        if commit:
            user.save()
        return user

