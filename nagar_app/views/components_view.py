from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from ..models import Notice, NoticeCategory
from .utils import user_is_admin

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