from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import Notice, NoticeCategory
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
