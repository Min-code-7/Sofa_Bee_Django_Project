from django.http import JsonResponse

# Create your views here.
def check_username(request):
    if request.method == "GET":
        username = request.GET.get("username")
        if not username:
            return JsonResponse({"error": "Username cannot be empty"}, status=400)
        
        # Check if username exists
        exists = User.objects.filter(username=username).exists()
        
        return JsonResponse({
            "exists": exists,
            "message": "Username already exists" if exists else "Username is available"
        })

import random
import time
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from django.utils import timezone
from .forms import UserRegisterForm
from .models import UserProfile

def send_verification_code(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            return JsonResponse({"error": "Email cannot be empty"}, status=400)

        # Check if a verification code was sent recently (within 1 minute)
        last_sent_time = request.session.get("verification_code_sent_time")
        if last_sent_time:
            last_sent = datetime.fromtimestamp(last_sent_time)
            time_diff = datetime.now() - last_sent
            if time_diff.total_seconds() < 60:  # 1 minute cooldown
                seconds_left = 60 - int(time_diff.total_seconds())
                return JsonResponse({
                    "error": f"Please wait {seconds_left} seconds before requesting a new code",
                    "seconds_left": seconds_left
                }, status=429)

        # Generate a 6-digit random verification code
        code = str(random.randint(100000, 999999))
        
        # Save code, email and timestamps in session
        request.session["verification_code"] = code
        request.session["email"] = email
        request.session["verification_code_sent_time"] = datetime.now().timestamp()
        request.session["verification_code_expiry_time"] = (datetime.now() + timedelta(minutes=5)).timestamp()

        # send email
        send_mail(
            subject="Register verification code",
            message=f"Your verification code is: {code}. Please complete the registration within 5 minutes.",
            from_email="itforpurchasing@163.com",  
            recipient_list=[email],
            fail_silently=False,
        )

        return JsonResponse({
            "message": "The verification code has been sent, please check your email!",
            "sent_time": request.session["verification_code_sent_time"]
        })

def register(request):
    user_type = request.GET.get("user_type", "regular")
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        print("Form submitted, validation result:", form.is_valid())
        if not form.is_valid():
            print("Form validation errors:", form.errors)
        
        if form.is_valid():
            email = form.cleaned_data["email"]
            input_code = form.cleaned_data["verification_code"]
            real_code = request.session.get("verification_code")
            expiry_time = request.session.get("verification_code_expiry_time")
            
            print(f"Input verification code: {input_code}")
            print(f"Verification code in session: {real_code}")

            # Check if verification code has expired
            if expiry_time and datetime.now().timestamp() > expiry_time:
                messages.error(request, "Verification code has expired! Please request a new one.")
                return redirect("users:register")

            if input_code != real_code:
                messages.error(request, "Verification code error!")
                print("Verification code does not match")
                return redirect("users:register")

            # Create user
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data["password"])
                user.save()
                print(f"User created: {user.username}")
                
                # Create UserProfile
                profile = UserProfile.objects.create(
                    user=user,
                    user_type=form.cleaned_data["user_type"],
                    phone_number=form.cleaned_data["phone_number"]
                )
                print(f"User profile created: {profile}")
                
                # Login
                login(request, user)
                print("User logged in")
                
                # Clear verification code data from session
                if "verification_code" in request.session:
                    del request.session["verification_code"]
                if "verification_code_sent_time" in request.session:
                    del request.session["verification_code_sent_time"]
                if "verification_code_expiry_time" in request.session:
                    del request.session["verification_code_expiry_time"]
                
                return redirect("products:product_list")
            except Exception as e:
                print(f"Error creating user: {e}")
                messages.error(request, f"Registration failed: {e}")
    else:
        form = UserRegisterForm(initial={'user_type': user_type})  # Ensure code is here

    return render(request, "users/register.html", {"form": form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('products:product_list')  
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})
    # return render(request, 'user:login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('products:product_list')
