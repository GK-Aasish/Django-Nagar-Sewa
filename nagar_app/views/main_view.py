from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .utils import user_is_admin
from ..models import Notice


def dashboard_view(request):
    return render(request, 'main/dashboard.html')

@login_required
def setting_view(request):
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        # Check current password
        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("setting")

        # Check new passwords match
        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("setting")

        # Set new password
        user.set_password(new_password)
        user.save()

        # Keep user logged in
        update_session_auth_hash(request, user)

        messages.success(request, "Password changed successfully.")
        return redirect("setting")
    else:
        return render(request,'main/settings.html')

def notice_view(request):
    notices = Notice.objects.all().order_by('-created_at')
    context = {"is_admin": user_is_admin(request.user)}
    return render(request,'main/notice.html',{'notices':notices,'context':context})