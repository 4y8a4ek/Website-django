from django import forms
from .models import UserProfile

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['photo']
