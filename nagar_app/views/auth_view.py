from django.shortcuts import render,redirect

def signup_module(request):
    return render(request,'auth/signup.html')