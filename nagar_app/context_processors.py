from .models import Profile


def user_profile(request):
    if request.user.is_authenticated:
        profile = Profile.objects.filter(user=request.user).first()
        return {"user_profile": profile}
    return {}
