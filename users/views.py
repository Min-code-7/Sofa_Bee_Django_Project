from django.http import JsonResponse

# Create your views here.
import random
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.contrib import messages
from .forms import UserRegisterForm

def send_verification_code(request):
    if request.method == "POST":
        email = request.POST.get("email")
        if not email:
            return JsonResponse({"error": "Email cannot be empty"}, status=400)

        # Generate a 6-digit random verification code
        code = str(random.randint(100000, 999999))
        request.session["verification_code"] = code  # save in session 
        request.session["email"] = email  # Record email addresses to prevent users from bypassing verification codes

        # send email
        send_mail(
            subject="register vertification code",
            message=f"Your vertification code is：{code}, Please complete the registration within 5 minutes.",
            from_email="itforpurchasing@163.com",  
            recipient_list=[email],
            fail_silently=False,
        )

        return JsonResponse({"message": "The verification code has been sent, please check your email!"})

def register(request):
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            input_code = form.cleaned_data["verification_code"]
            real_code = request.session.get("verification_code")

            if input_code != real_code:
                messages.error(request, "Wrong vertification code!")
                return redirect("register")

            # create user
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()

            # login
            login(request, user)
            return redirect("home")

    else:
        form = UserRegisterForm()

    return render(request, "users/register.html", {"form": form})

def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')  # redirect to home
    else:
        form = AuthenticationForm()
    return render(request, 'users/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('home')