from django.shortcuts import render,redirect

def signup_module(request):
    return render(request,'auth/signup.html')

def login_model(request):
    return render(request,'auth/login.html')