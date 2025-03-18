import string
from email.policy import default
from tkinter import image_names

from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from pyexpat.errors import messages
import random
from django.core.mail import send_mail

from addresses.models import Address
from .models import Order, Payment, Order_Item
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
    send_mail("Sofa Bee Registration Verification Code", message=f"your register verification code is：{captcha}", recipient_list=[email],from_email=None)
    return JsonResponse({"code": 200, "message": "send success！"})


def compare_code(request):
    email=request.GET.get('email')
    user_captcha=request.GET.get('captcha')
    info=CaptchaModel.objects.filter(email=email).first()

    if not user_captcha:
        return JsonResponse({"code":400,"message":"verification code is empty"})
    if info is not None:
        if user_captcha==info.captcha:
            return JsonResponse({"code": 200, "message": "verification code is correct！"})
        else:
            return JsonResponse({"code": 400, "message": "verification code is wrong！"})




def history_order(request, id):
    orders = Order.objects.filter(consumer_id=id)
    order_infos = []

    class Detail:
        def __init__(self, shop_name, product_name, image, item_price, item_quantity, unit_price, price):
            self.shop_name = shop_name
            self.product_name = product_name
            self.image = image
            self.item_price = item_price
            self.item_quantity = item_quantity
            self.unit_price = unit_price
            self.price = price

    class OrderInfo:
        def __init__(self, order_id, order_time, order_status, total_price, paid_status, details):
            self.order_id = order_id
            self.total_price = total_price
            self.paid_status = paid_status
            self.order_time = order_time
            self.order_status = order_status
            self.details = details

    for order in orders:
        payment = Payment.objects.get(order=order)

        order_items = Order_Item.objects.filter(order=order)
        details_1 = []

        for item in order_items:
            # products.append(item.product)
            detail = Detail(
                shop_name=item.product.merchant.shop_name,
                product_name=item.product.name,
                image=item.product.image,
                item_price=item.price,
                item_quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )

            details_1.append(detail)
        order_info = OrderInfo(order_id=order.id, order_time=order.order_time, order_status=order.order_status,
                               total_price=order.total_price, paid_status=payment.paid_status, details=details_1)
        print(len(details_1))
        order_infos.append(order_info)
        print(len(order_infos))
    order_number = request.GET.get('q')
    filtered_order_infos=[]

    if order_number:
        filtered_order_infos = [
            order_info for order_info in order_infos
            if str(order_info.order_id) == order_number
        ]
    else:
        filtered_order_infos = order_infos
    return render(request, "history_orders.html", {'id': id, 'orders': filtered_order_infos})


def order_detail(request,id):
    #id获取order
    order=Order.objects.get(id=id)


    class OrderInfo:
        def __init__(self, order_id, order_time, order_status, paid_status,address,paid_time):
            self.order_id = order_id
            self.paid_status = paid_status
            self.order_time = order_time
            self.order_status = order_status
            self.address = address
            self.paid_time = paid_time
    payment=Payment.objects.get(order=order)
    address_1=order.address
    order_info=OrderInfo(order_id=order.id, order_time=order.order_time, order_status=order.order_status,paid_status=payment.paid_status,address=address_1,paid_time=payment.paid_time)

    class Final_detail:
        def __init__(self, item_name,picture,description,quantity,price,total_price):

            self.item_name = item_name
            self.picture = picture
            self.description = description
            self.quantity = quantity
            self.price = price
            self.total_price = total_price

    class Final_result:
        def __init__(self, merchant,final_details):
            self.merchant = merchant
            self.final_details = final_details
    order_items = Order_Item.objects.filter(order=order)  # 获取所有订单项
    products=[]
    #获得所有商品
    for order_item in order_items:
        product=order_item.product
        products.append(product)
    #获得所有店家
    merchants=[]
    for product in products:
        merchant=product.merchant
        merchants.append(merchant)

    final_results=[]
    merchants = list({product_1.merchant.id: product_1.merchant for product_1 in products}.values())
    for merchant in merchants:
        final_details=[]
        for product in products:
            if product.merchant_id == merchant.id:
                name=product.name
                picture=product.image
                description=product.description
                order_item=Order_Item.objects.get(product_id=product.id)
                unit_price=product.price
                quantity=order_item.quantity
                total_price=order_item.price
                final_detail=Final_detail(name,picture,description,quantity,unit_price,total_price)
                final_details.append(final_detail)
        final_result=Final_result(merchant,final_details)
        final_results.append(final_result)

    return render(request,'order_detail.html',{'order_info':order_info,'final_results':final_results})