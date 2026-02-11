from datetime import timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Q

from .utils import user_is_admin
from ..models import (
    Notice,
    NoticeReaction,
    ReactionType,
    NoticeCategory,
    Event,
    EventReaction,
    EventCategory,
    EventRegistration,
    Profile,
    Meeting,
    MeetingDocument,
)


def dashboard_view(request):
    """Dashboard page"""
    now = timezone.now()
    is_admin = user_is_admin(request.user)

    notices_count = Notice.objects.count()
    notices_week = Notice.objects.filter(created_at__gte=now - timedelta(days=7)).count()

    events_count = Event.objects.count()
    upcoming_events_count = Event.objects.filter(event_date__gte=now).count()

    meetings_count = Meeting.objects.count()
    upcoming_meetings_count = Meeting.objects.filter(meeting_date__gte=now).count()
    next_meeting = Meeting.objects.filter(meeting_date__gte=now).order_by('meeting_date').first()

    if request.user.is_authenticated:
        member_registrations_count = EventRegistration.objects.filter(user=request.user).count()
        admin_registrations_count = EventRegistration.objects.filter(event__author=request.user).count()
    else:
        member_registrations_count = 0
        admin_registrations_count = 0

    registrations_count = admin_registrations_count if is_admin else member_registrations_count

    upcoming_events = Event.objects.filter(event_date__gte=now).order_by('event_date')[:3]
    upcoming_meetings = Meeting.objects.filter(meeting_date__gte=now).order_by('meeting_date')[:3]
    latest_notices = Notice.objects.order_by('-created_at')[:4]

    context = {
        "notices_count": notices_count,
        "notices_week": notices_week,
        "events_count": events_count,
        "upcoming_events_count": upcoming_events_count,
        "meetings_count": meetings_count,
        "upcoming_meetings_count": upcoming_meetings_count,
        "next_meeting": next_meeting,
        "registrations_count": registrations_count,
        "member_registrations_count": member_registrations_count,
        "admin_registrations_count": admin_registrations_count,
        "upcoming_events": upcoming_events,
        "upcoming_meetings": upcoming_meetings,
        "latest_notices": latest_notices,
        "now": now,
        "is_admin": is_admin,
    }
    return render(request, 'main/dashboard.html', context)


def contact_view(request):
    """Contact page"""
    context = {
        "council_phone": "+00 000 000 0000",
        "council_email": "council@example.com",
        "council_address": "Village Council Office, Main Road",
        "council_hours": "Sun-Fri, 9:00 AM - 5:00 PM",
    }
    return render(request, 'main/contact.html', context)


@login_required
def setting_view(request):
    """User settings page (password change)"""
    profile, _ = Profile.objects.get_or_create(user=request.user)

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

    context = {
        "profile": profile,
    }
    return render(request, 'main/settings.html', context)


@login_required
def update_avatar_view(request):
    if request.method == "POST":
        profile, _ = Profile.objects.get_or_create(user=request.user)
        image = request.FILES.get("avatar")
        if image:
            profile.image = image
            profile.save()
            messages.success(request, "Profile image updated.")
        else:
            messages.error(request, "Please select an image to upload.")
    return redirect("setting")


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
def event_view(request):
    """Event board page with dynamic reactions"""
    events = Event.objects.annotate(
        like_count=Count('reactions', filter=Q(reactions__reaction_type__name='Like')),
        dislike_count=Count('reactions', filter=Q(reactions__reaction_type__name='Dislike'))
    ).order_by('-created_at')

    user_reactions = {}
    if request.user.is_authenticated:
        user_reactions = {
            r.event_id: r.reaction_type.name
            for r in EventReaction.objects.filter(user=request.user, event__in=events)
        }

    events_with_reactions = []
    for event in events:
        reaction = user_reactions.get(event.id)
        events_with_reactions.append({
            "event": event,
            "user_reaction": reaction
        })

    categories = EventCategory.objects.all()

    context = {
        "events_with_reactions": events_with_reactions,
        "categories": categories,
        "is_admin": user_is_admin(request.user),
    }
    return render(request, 'main/event.html', context)


@login_required
def meeting_view(request):
    meetings = Meeting.objects.select_related('author').prefetch_related('documents').order_by('-meeting_date')
    context = {
        "meetings": meetings,
        "is_admin": user_is_admin(request.user),
        "now": timezone.now(),
    }
    return render(request, 'main/meetings.html', context)


@login_required
def meeting_detail_view(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)
    documents = meeting.documents.all().order_by('-uploaded_at')
    context = {
        "meeting": meeting,
        "documents": documents,
        "is_admin": user_is_admin(request.user),
        "now": timezone.now(),
    }
    return render(request, 'main/meeting_detail.html', context)


@login_required
def delete_meeting_view(request, meeting_id):
    if not user_is_admin(request.user):
        messages.error(request, "You do not have permission to delete meetings.")
        return redirect('meeting_detail', meeting_id=meeting_id)

    meeting = get_object_or_404(Meeting, id=meeting_id)

    if request.method == "POST":
        meeting.delete()
        messages.success(request, "Meeting deleted successfully.")
        return redirect('meeting')

    return redirect('meeting_detail', meeting_id=meeting_id)


@login_required
def delete_meeting_document_view(request, doc_id):
    if not user_is_admin(request.user):
        messages.error(request, "You do not have permission to delete documents.")
        return redirect('meeting')

    doc = get_object_or_404(MeetingDocument, id=doc_id)
    meeting_id = doc.meeting_id

    if request.method == "POST":
        doc.delete()
        messages.success(request, "Document deleted successfully.")
        return redirect('meeting_detail', meeting_id=meeting_id)

    return redirect('meeting_detail', meeting_id=meeting_id)


@login_required
def meeting_document_detail_view(request, doc_id):
    doc = get_object_or_404(MeetingDocument, id=doc_id)
    if doc.document_type != "image":
        return redirect('meeting_detail', meeting_id=doc.meeting_id)

    images = list(
        MeetingDocument.objects.filter(
            meeting=doc.meeting,
            document_type="image"
        ).order_by('uploaded_at', 'id')
    )
    image_ids = [d.id for d in images]
    current_index = image_ids.index(doc.id)
    prev_doc = images[current_index - 1] if current_index > 0 else None
    next_doc = images[current_index + 1] if current_index + 1 < len(images) else None

    context = {
        "meeting": doc.meeting,
        "doc": doc,
        "images": images,
        "prev_doc": prev_doc,
        "next_doc": next_doc,
        "current_index": current_index + 1,
        "total_images": len(images),
    }
    return render(request, 'main/meeting_document_detail.html', context)


@login_required
def upload_meeting_document_view(request, meeting_id):
    meeting = get_object_or_404(Meeting, id=meeting_id)

    if not user_is_admin(request.user):
        messages.error(request, "You do not have permission to upload documents.")
        return redirect('meeting')

    if meeting.meeting_date > timezone.now():
        messages.error(request, "You can upload documents only after the meeting ends.")
        return redirect('meeting')

    if request.method == "POST":
        document_type = request.POST.get("document_type")
        file = request.FILES.get("file")

        if not document_type or not file:
            messages.error(request, "Please select a document type and file.")
            return redirect('upload_meeting_document', meeting_id=meeting.id)

        MeetingDocument.objects.create(
            meeting=meeting,
            document_type=document_type,
            file=file,
            uploaded_by=request.user
        )
        messages.success(request, "Document uploaded successfully.")
        return redirect('meeting')

    context = {
        "meeting": meeting,
        "documents": meeting.documents.all().order_by('-uploaded_at')
    }
    return render(request, 'main/upload_meeting_document.html', context)


@login_required
def event_detail_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    like_count = EventReaction.objects.filter(event=event, reaction_type__name='Like').count()
    dislike_count = EventReaction.objects.filter(event=event, reaction_type__name='Dislike').count()

    registrations = EventRegistration.objects.filter(event=event).select_related("user").order_by("-registered_at")
    registration_count = registrations.count()
    is_registered = registrations.filter(user=request.user).exists()
    user_reaction = None
    if request.user.is_authenticated:
        user_reaction = EventReaction.objects.filter(event=event, user=request.user).values_list(
            "reaction_type__name", flat=True
        ).first()

    context = {
        "event": event,
        "like_count": like_count,
        "dislike_count": dislike_count,
        "user_reaction": user_reaction,
        "is_admin": user_is_admin(request.user),
        "is_registered": is_registered,
        "registrations": registrations,
        "registration_count": registration_count,
    }
    return render(request, 'main/event_detail.html', context)


@login_required
def register_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        registration = EventRegistration.objects.filter(
            event=event,
            user=request.user
        ).first()
        if registration:
            registration.delete()
            messages.info(request, "Your registration has been canceled.")
        else:
            EventRegistration.objects.create(event=event, user=request.user)
            messages.success(request, "You have registered for this event.")
        return redirect('event_detail', event_id=event.id)

    return redirect('event_detail', event_id=event.id)


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


@login_required
def react_to_event(request):
    """
    AJAX view to handle Like/Dislike reactions for events
    - Toggle reaction if already exists
    - Only one reaction per user per event
    """
    if request.method == "POST":
        event_id = request.POST.get("event_id")
        reaction_name = request.POST.get("reaction")

        event = get_object_or_404(Event, id=event_id)
        reaction_type = get_object_or_404(ReactionType, name=reaction_name)
        user = request.user

        existing_reaction = EventReaction.objects.filter(event=event, user=user).first()

        if existing_reaction:
            if existing_reaction.reaction_type == reaction_type:
                existing_reaction.delete()
            else:
                existing_reaction.reaction_type = reaction_type
                existing_reaction.save()
        else:
            EventReaction.objects.create(event=event, user=user, reaction_type=reaction_type)

        like_count = EventReaction.objects.filter(event=event, reaction_type__name='Like').count()
        dislike_count = EventReaction.objects.filter(event=event, reaction_type__name='Dislike').count()

        return JsonResponse({
            "like_count": like_count,
            "dislike_count": dislike_count,
        })

    return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
def delete_notice_view(request, notice_id):
    if not user_is_admin(request.user):
        messages.error(request, "You do not have permission to delete notices.")
        return redirect('notice')

    notice = get_object_or_404(Notice, id=notice_id)

    if request.method == "POST":
        notice.delete()
        messages.success(request, "Notice deleted successfully.")
        return redirect('notice')

    # Optional: Render a confirmation page instead of JS confirm
    return render(request, 'main/confirm_delete.html', {'notice': notice})


@login_required
def delete_event_view(request, event_id):
    if not user_is_admin(request.user):
        messages.error(request, "You do not have permission to delete events.")
        return redirect('event')

    event = get_object_or_404(Event, id=event_id)

    if request.method == "POST":
        event.delete()
        messages.success(request, "Event deleted successfully.")
        return redirect('event')

    return render(request, 'main/confirm_delete.html', {'event': event})
