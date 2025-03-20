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

import socket
import smtplib
from django.conf import settings

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

        # Debug information
        print(f"Sending verification code {code} to {email}")
        print(f"Email settings: HOST={settings.EMAIL_HOST}, PORT={settings.EMAIL_PORT}, USER={settings.EMAIL_HOST_USER}")
        print(f"SSL={settings.EMAIL_USE_SSL}, TLS={settings.EMAIL_USE_TLS}")
        
        try:
            # Test SMTP connection first
            try:
                if settings.EMAIL_USE_SSL:
                    smtp = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
                else:
                    smtp = smtplib.SMTP(settings.EMAIL_HOST, settings.EMAIL_PORT, timeout=10)
                
                if settings.EMAIL_USE_TLS:
                    smtp.starttls()
                
                # Try to login
                smtp.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
                print("SMTP connection and login successful")
                smtp.quit()
            except (socket.error, smtplib.SMTPException) as e:
                print(f"SMTP connection test failed: {str(e)}")
                # Continue anyway to see the actual Django error
            
            # Send email using Django's send_mail
            send_mail(
                subject="Register verification code",
                message=f"Your verification code is: {code}. Please complete the registration within 5 minutes.",
                from_email=settings.EMAIL_HOST_USER,  
                recipient_list=[email],
                fail_silently=False,
            )
            print(f"Email sent successfully to {email}")
            
            return JsonResponse({
                "message": "The verification code has been sent, please check your email!",
                "sent_time": request.session["verification_code_sent_time"]
            })
        except Exception as e:
            error_msg = str(e)
            print(f"Failed to send email: {error_msg}")
            
            # Provide more specific error messages based on common SMTP issues
            if "Authentication" in error_msg:
                error_details = "Email authentication failed. The password or authorization code may be incorrect."
            elif "timed out" in error_msg:
                error_details = "Connection to email server timed out. Check network settings or firewall."
            elif "Unknown SMTP host" in error_msg:
                error_details = "Could not connect to email server. Check the host name."
            elif "Connection refused" in error_msg:
                error_details = "Email server refused connection. Check port settings and server availability."
            else:
                error_details = error_msg
            
            # For debugging purposes, still save the code in session and return it
            # In production, you would want to return a generic error instead
            return JsonResponse({
                "message": f"Verification code is {code} (displayed for debugging). In production, this would be sent via email.",
                "debug_code": code,  # Only for debugging
                "error_details": error_details,
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
