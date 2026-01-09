from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Count, Q

from .utils import user_is_admin
from ..models import Notice, NoticeReaction, ReactionType, NoticeCategory


def dashboard_view(request):
    """Dashboard page"""
    return render(request, 'main/dashboard.html')


@login_required
def setting_view(request):
    """User settings page (password change)"""
    if request.method == "POST":
        current_password = request.POST.get("current_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        user = request.user

        if not user.check_password(current_password):
            messages.error(request, "Current password is incorrect.")
            return redirect("setting")

        if new_password != confirm_password:
            messages.error(request, "New passwords do not match.")
            return redirect("setting")

        user.set_password(new_password)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, "Password changed successfully.")
        return redirect("setting")

    return render(request, 'main/settings.html')


@login_required
def notice_view(request):
    """Notice board page with dynamic reactions"""
    # Annotate notices with like and dislike counts
    notices = Notice.objects.annotate(
        like_count=Count('reactions', filter=Q(reactions__reaction_type__name='Like')),
        dislike_count=Count('reactions', filter=Q(reactions__reaction_type__name='Dislike'))
    ).order_by('-created_at')

    # Get current user's reactions for highlighting
    user_reactions = {}
    if request.user.is_authenticated:
        user_reactions = {
            r.notice_id: r.reaction_type.name
            for r in NoticeReaction.objects.filter(user=request.user, notice__in=notices)
        }

    # Combine notices and reactions in a list for the template
    notices_with_reactions = []
    for notice in notices:
        reaction = user_reactions.get(notice.id)  # Could be None, 'Like', or 'Dislike'
        notices_with_reactions.append({
            "notice": notice,
            "user_reaction": reaction
        })

    categories = NoticeCategory.objects.all()

    context = {
        "notices_with_reactions": notices_with_reactions,
        "categories": categories,
        "is_admin": user_is_admin(request.user),
    }
    return render(request, 'main/notice.html', context)


@login_required
def react_to_notice(request):
    """
    AJAX view to handle Like/Dislike reactions
    - Toggle reaction if already exists
    - Only one reaction per user per notice
    """
    if request.method == "POST":
        notice_id = request.POST.get("notice_id")
        reaction_name = request.POST.get("reaction")

        notice = get_object_or_404(Notice, id=notice_id)
        reaction_type = get_object_or_404(ReactionType, name=reaction_name)
        user = request.user

        # Check if the user already reacted
        existing_reaction = NoticeReaction.objects.filter(notice=notice, user=user).first()

        if existing_reaction:
            if existing_reaction.reaction_type == reaction_type:
                # Same reaction clicked again → remove reaction
                existing_reaction.delete()
            else:
                # Different reaction → update
                existing_reaction.reaction_type = reaction_type
                existing_reaction.save()
        else:
            # No reaction yet → create
            NoticeReaction.objects.create(notice=notice, user=user, reaction_type=reaction_type)

        # Return updated counts
        like_count = NoticeReaction.objects.filter(notice=notice, reaction_type__name='Like').count()
        dislike_count = NoticeReaction.objects.filter(notice=notice, reaction_type__name='Dislike').count()

        return JsonResponse({
            "like_count": like_count,
            "dislike_count": dislike_count,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)
