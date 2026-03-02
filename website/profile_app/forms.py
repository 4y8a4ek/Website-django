from django import forms
from .models import UserProfile

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo']


class ProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['birth_date', 'phone', 'city']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }