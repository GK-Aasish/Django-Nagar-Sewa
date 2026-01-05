
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.models import User

def login_module(request):
    errors = {}
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not email:
            errors['email'] = "Email field is Required"
        elif not User.objects.filter(username=email).exists():
            errors['email'] = "Email does not exist ! please signup first"

        if not password:
            errors['password'] = "Password is required"

        if errors:
            return render(request, 'auth/login.html', {'errors': errors,'data':request.POST})
        
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
    else:
        errors['username'] = "Invalid login credentials"
        errors['password'] = "Invalid login credentials"
        return render(request, 'auth/login.html', {'errors': errors,'data':request.POST})

def signup_module(request):
    errors = {}
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')

        # print(username,email,password,confirm)
        if not firstname:
            errors['firstname'] = "firstname is Required"

        if not lastname:
            errors['lastname'] = "lastname is Required"

        if not email:
            errors['email'] = "Email field is Required"
        elif User.objects.filter(username=email).exists():
            errors['email'] = "Email already exists ! user another email"
        
        if not password:
            errors['password'] = "Password is required"
        elif len(password) <=6:
            errors['password']= "Password contains more than 6 characters"

        if not confirm:
            errors['confirm'] = " Confirm Password is required"

        if password != confirm:
            errors['confirm'] = "Confirm password not matched !!"

        if errors:
            return render(request, 'auth/signup.html', {'errors': errors,'data':request.POST})
        
        else:
            user = User.objects.create_user(
                username=email,
                first_name=firstname,
                last_name=lastname,
                password=password,
            )
            messages.success(request,'User Registration Successfully !! ')
            return redirect('login')

        
    else:
        # first ma register page display huda
        return render(request, 'auth/signup.html')

    
