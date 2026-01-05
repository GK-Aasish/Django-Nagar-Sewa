from django.shortcuts import render,redirect

def dashboard_view(request):
    return render(request, 'main/dashboard.html')