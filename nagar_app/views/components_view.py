from datetime import datetime
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from ..models import Notice, NoticeCategory, Event, EventCategory, Meeting
from .utils import user_is_admin
from django.contrib.auth.decorators import login_required

@login_required
def add_notice_model(request):
    if not user_is_admin(request.user):
        return redirect('notice')  # only admins allowed

    errors = {}
    categories = NoticeCategory.objects.all()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category_id = request.POST.get("category")

        # Basic validation
        if not title:
            errors['title'] = "Title is required"
        if not description:
            errors['description'] = "Description is required"
        if not category_id:
            errors['category'] = "Category is required"

        if not errors:
            try:
                category = get_object_or_404(NoticeCategory, id=category_id)
                Notice.objects.create(
                    title=title,
                    description=description,
                    category=category,
                    author=request.user
                )
                messages.success(request, "Notice created successfully!")
                return redirect('notice')
            except Exception as e:
                messages.error(request, f"Failed to create notice: {e}")

        else:
            return render(request,'components/add_notice.html',{'errors':errors,'data':request.POST,'categories': categories})
        
    return render(request, 'components/add_notice.html', {'categories': categories})

@login_required
def edit_notice_view(request, notice_id):
    # Fetch the existing notice
    notice = get_object_or_404(Notice, id=notice_id)

    # Only admin can edit
    if not user_is_admin(request.user):
        messages.error(request, "You do not have permission to edit notices.")
        return redirect('notice')

    error = {}

    if request.method == "POST":
        title = request.POST.get('title')
        category_id = request.POST.get('category')
        description = request.POST.get('description')

        # Validation
        if not title:
            error['title'] = "Title is required."
        if not category_id:
            error['category'] = "Category is required."
        if not description:
            error['description'] = "Description is required."

        if error:
            categories = NoticeCategory.objects.all()
            return render(request, 'components/edit_notice.html', {
                'notice': notice,
                'categories': categories,
                'error': error
            })

        # Update notice
        notice.title = title
        notice.category = get_object_or_404(NoticeCategory, id=category_id)
        notice.description = description
        notice.save()

        messages.success(request, "Notice updated successfully.")
        return redirect('notice')

    # GET request → render form with existing data
    categories = NoticeCategory.objects.all()
    return render(request, 'components/edit_notice.html', {
        'notice': notice,
        'categories': categories,
        'error': error
    })

@login_required
def cancel_edit(request, notice_id):
    notice = get_object_or_404(Notice, id=notice_id)

    # Optional: admin check
    if not user_is_admin(request.user):
        messages.error(request, "Unauthorized access.")
        return redirect('notice')

    return render(request, 'components/cancel_edit.html', {
        'notice': notice
    })


def _parse_event_date(value):
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    if settings.USE_TZ and timezone.is_naive(parsed):
        return timezone.make_aware(parsed, timezone.get_current_timezone())
    return parsed


@login_required
def add_event_view(request):
    if not user_is_admin(request.user):
        return redirect('event')

    errors = {}
    categories = EventCategory.objects.all()

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        category_id = request.POST.get("category")
        event_date_str = request.POST.get("event_date", "").strip()
        location = request.POST.get("location", "").strip()
        image = request.FILES.get("image")

        if not title:
            errors['title'] = "Title is required"
        if not description:
            errors['description'] = "Description is required"
        if not category_id:
            errors['category'] = "Category is required"
        if not event_date_str:
            errors['event_date'] = "Event date is required"
        if not location:
            errors['location'] = "Location is required"

        event_date = _parse_event_date(event_date_str)
        if event_date_str and not event_date:
            errors['event_date'] = "Invalid date/time format"

        if not errors:
            try:
                category = get_object_or_404(EventCategory, id=category_id)
                Event.objects.create(
                    title=title,
                    description=description,
                    category=category,
                    event_date=event_date,
                    location=location,
                    image=image,
                    author=request.user
                )
                messages.success(request, "Event created successfully!")
                return redirect('event')
            except Exception as e:
                messages.error(request, f"Failed to create event: {e}")
        else:
            return render(request, 'components/add_event.html', {
                'errors': errors,
                'data': request.POST,
                'categories': categories
            })

    return render(request, 'components/add_event.html', {'categories': categories})


@login_required
def edit_event_view(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if not user_is_admin(request.user):
        messages.error(request, "You do not have permission to edit events.")
        return redirect('event')

    error = {}

    if request.method == "POST":
        title = request.POST.get('title', "").strip()
        category_id = request.POST.get('category')
        description = request.POST.get('description', "").strip()
        event_date_str = request.POST.get("event_date", "").strip()
        location = request.POST.get("location", "").strip()
        image = request.FILES.get("image")

        if not title:
            error['title'] = "Title is required."
        if not category_id:
            error['category'] = "Category is required."
        if not description:
            error['description'] = "Description is required."
        if not event_date_str:
            error['event_date'] = "Event date is required."
        if not location:
            error['location'] = "Location is required."

        event_date = _parse_event_date(event_date_str)
        if event_date_str and not event_date:
            error['event_date'] = "Invalid date/time format"

        if error:
            categories = EventCategory.objects.all()
            return render(request, 'components/edit_event.html', {
                'event': event,
                'categories': categories,
                'error': error
            })

        event.title = title
        event.category = get_object_or_404(EventCategory, id=category_id)
        event.description = description
        event.event_date = event_date
        event.location = location
        if image:
            event.image = image
        event.save()

        messages.success(request, "Event updated successfully.")
        return redirect('event')

    categories = EventCategory.objects.all()
    return render(request, 'components/edit_event.html', {
        'event': event,
        'categories': categories,
        'error': error
    })


@login_required
def add_meeting_view(request):
    if not user_is_admin(request.user):
        return redirect('meeting')

    errors = {}

    if request.method == "POST":
        title = request.POST.get("title", "").strip()
        description = request.POST.get("description", "").strip()
        meeting_date_str = request.POST.get("meeting_date", "").strip()
        location = request.POST.get("location", "").strip()

        if not title:
            errors['title'] = "Title is required"
        if not description:
            errors['description'] = "Description is required"
        if not meeting_date_str:
            errors['meeting_date'] = "Meeting date is required"
        if not location:
            errors['location'] = "Location is required"

        meeting_date = _parse_event_date(meeting_date_str)
        if meeting_date_str and not meeting_date:
            errors['meeting_date'] = "Invalid date/time format"

        if not errors:
            try:
                Meeting.objects.create(
                    title=title,
                    description=description,
                    meeting_date=meeting_date,
                    location=location,
                    author=request.user
                )
                messages.success(request, "Meeting created successfully!")
                return redirect('meeting')
            except Exception as e:
                messages.error(request, f"Failed to create meeting: {e}")
        else:
            return render(request, 'components/add_meeting.html', {
                'errors': errors,
                'data': request.POST,
            })

    return render(request, 'components/add_meeting.html')
