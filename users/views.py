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
from .models import UserProfile

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

# def register(request):
    # user_type = request.GET.get("user_type", "regular")
    # if request.method == "POST":
        # form = UserRegisterForm(request.POST)
        # if form.is_valid():
            # email = form.cleaned_data["email"]
            # input_code = form.cleaned_data["verification_code"]
            # real_code = request.session.get("verification_code")

            # if input_code != real_code:
                # messages.error(request, "Wrong vertification code!")
                # return redirect("register")

            # # create user
            # user = form.save(commit=False)
            # user.set_password(form.cleaned_data["password"])
            # user.save()
            
            # # create UserProfile to connect to User
            # user_profile = UserProfile.objects.create(
                # user=user,
                # user_type=form.cleaned_data["user_type"],
                # phone_number=form.cleaned_data["phone_number"]
            # )

            # # login
            # login(request, user)
            # return redirect("products:product_list")

    # else:
        # form = UserRegisterForm(initial={'user_type': user_type})

    # return render(request, "users/register.html", {"form": form})
    
def register(request):
    user_type = request.GET.get("user_type", "regular")
    if request.method == "POST":
        form = UserRegisterForm(request.POST)
        print("表单提交了，验证结果:", form.is_valid())
        if not form.is_valid():
            print("表单验证错误:", form.errors)
        
        if form.is_valid():
            email = form.cleaned_data["email"]
            input_code = form.cleaned_data["verification_code"]
            real_code = request.session.get("verification_code")
            
            print(f"输入的验证码: {input_code}")
            print(f"session中的验证码: {real_code}")

            if input_code != real_code:
                messages.error(request, "验证码错误!")
                print("验证码不匹配")
                return redirect("users:register")

            # 创建用户
            try:
                user = form.save(commit=False)
                user.set_password(form.cleaned_data["password"])
                user.save()
                print(f"用户已创建: {user.username}")
                
                # 创建UserProfile
                profile = UserProfile.objects.create(
                    user=user,
                    user_type=form.cleaned_data["user_type"],
                    phone_number=form.cleaned_data["phone_number"]
                )
                print(f"用户资料已创建: {profile}")
                
                # 登录
                login(request, user)
                print("用户已登录")
                return redirect("products:product_list")
            except Exception as e:
                print(f"创建用户时出错: {e}")
                messages.error(request, f"注册失败: {e}")
    else:
        form = UserRegisterForm(initial={'user_type': user_type})  # 确保这里有代码

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

def user_logout(request):
    logout(request)
    return redirect('products:product_list')