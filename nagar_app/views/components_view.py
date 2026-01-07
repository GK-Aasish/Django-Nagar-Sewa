from django.shortcuts import render,redirect

def add_notice_model(request):
    return render(request,'components/add_notice.html')