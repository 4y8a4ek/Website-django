# user_auth/decorators.py
from django.shortcuts import redirect

def profile_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            profile = getattr(request.user, 'userprofile', None)
            if profile and not profile.is_complete():
                return redirect('user_auth:profile_fill')
        return view_func(request, *args, **kwargs)
    return wrapper