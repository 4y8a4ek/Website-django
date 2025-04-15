from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import PhotoUploadForm

@login_required
def profile_view(request):
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('profile_app:profile')
    else:
        form = PhotoUploadForm(instance=profile)

    return render(request, 'profile.html', {
        'profile': profile,
        'form': form
    })
