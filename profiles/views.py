import string
from email.policy import default
from tkinter import image_names

from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from pyexpat.errors import messages
import random
from django.core.mail import send_mail

from addresses.models import Address
from profiles.models import CaptchaModel
from users.models import Consumer
# Create your views here.
def profiles(request,id):
    user=Consumer.objects.get(id=id)
    addresses = Address.objects.filter(consumer_id=id, is_default=True)


    return render(request,'profile.html',{'user':user,'addresses':addresses})


def modify(request,id):
    user=Consumer.objects.get(id=id)

    if request.method=='POST':
        name=request.POST.get('name')
        if name is None:
            name=user.name
        email=request.POST.get('email')
        if request.POST.get('new-email'):
            email=request.POST.get('new-email')
        phone=request.POST.get('phone')
        if phone is None:
            phone = user.phone

        Consumer.objects.filter(id=id).update(name=name,email=email,phone=phone)

        return redirect('modify_profile', id=id)

    return render(request,'modify.html',{'user':user})

def send_email_captcha(request,id):
    # ?email=xxx
    email = request.GET.get('email')
    if not email:
        return JsonResponse({"code": 400, "message": '必须传递邮箱！'})
    captcha = "".join(random.sample(string.digits, 4))
    # 存储到数据库中
    CaptchaModel.objects.update_or_create(email=email, defaults={'captcha': captcha})
    send_mail("知了博客注册验证码", message=f"您的注册验证码是：{captcha}", recipient_list=[email],from_email=None)
    return JsonResponse({"code": 200, "message": "邮箱验证码发送成功！"})


def compare_code(request):
    email=request.GET.get('email')
    user_captcha=request.GET.get('captcha')
    info=CaptchaModel.objects.filter(email=email).first()

    if not user_captcha:
        return JsonResponse({"code":400,"message":"验证码为空"})
    if info is not None:
        if user_captcha==info.captcha:
            return JsonResponse({"code": 200, "message": "验证码正确！"})
        else:
            return JsonResponse({"code": 400, "message": "验证码错误！"})



