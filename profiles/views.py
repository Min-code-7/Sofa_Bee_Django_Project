import string
from email.policy import default
from tkinter import image_names

from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from pyexpat.errors import messages
import random
from django.core.mail import send_mail

from addresses.models import Address

from orders.models import OrderItem, Order
from profiles.models import CaptchaModel

from users.models import UserProfile


# Create your views here.
def profiles(request, id):
    userProfile = UserProfile.objects.get(id=id)
    # if the account type is normal  user
    if userProfile.user_type == "regular":
        addresses = Address.objects.get(userProfile.user.id)
        return render(request, 'profile.html', {'user': userProfile.user, 'addresses': addresses})

    # accout is merchant
    user = userProfile.user.get(id=id)
    addresses = Address.objects.filter(consumer_id=id, is_default=True)
    return render(request, 'profile.html', {'user': user, 'addresses': addresses})


def modify(request, id):
    userProfile = UserProfile.objects.get(id=id)
    user = userProfile.user
    if request.method == 'POST':
        name = request.POST.get('name')
        if name is None:
            name = user.name
        email = request.POST.get('email')
        if request.POST.get('new-email'):
            email = request.POST.get('new-email')
        phone = request.POST.get('phone')
        if phone is None:
            phone = user.phone

        User.objects.filter(id=id).update(name=name, email=email, phone=phone)

        return redirect('modify_profile', id=id)

    return render(request, 'modify.html', {'user': user})


def send_email_captcha(request, id):
    # ?email=xxx
    email = request.GET.get('email')
    if not email:
        return JsonResponse({"code": 400, "message": '必须传递邮箱！'})
    captcha = "".join(random.sample(string.digits, 4))
    # 存储到数据库中
    CaptchaModel.objects.update_or_create(email=email, defaults={'captcha': captcha})
    send_mail("Sofa Bee Registration Verification Code", message=f"your register verification code is：{captcha}",
              recipient_list=[email], from_email=None)
    return JsonResponse({"code": 200, "message": "send success！"})


def compare_code(request):
    email = request.GET.get('email')
    user_captcha = request.GET.get('captcha')
    info = CaptchaModel.objects.filter(email=email).first()

    if not user_captcha:
        return JsonResponse({"code": 400, "message": "verification code is empty"})
    if info is not None:
        if user_captcha == info.captcha:
            return JsonResponse({"code": 200, "message": "verification code is correct！"})
        else:
            return JsonResponse({"code": 400, "message": "verification code is wrong！"})


def history_order(request, id):
    orders = Order.objects.filter(consumer_id=id)

    order_infos = []

    class Detail:
        def __init__(self, product_name, image, item_price, quantity, price, shop_name):
            self.product_name = product_name
            self.image = image
            self.item_price = item_price
            self.item_quantity = quantity
            self.price = price
            self.shop_name = shop_name

    class OrderInfo:
        def __init__(self, order_id, order_number, total_price, status, payment_method, created_at, details, paid_at):
            self.order_id = order_id
            self.order_number = order_number
            self.total_price = total_price
            self.status = status
            self.payment_method = payment_method
            self.created_at = created_at
            self.details = details
            self.paid_at = paid_at


    for order in orders:
        # payment = Payment.objects.get(order=order)
        order_items = OrderItem.objects.filter(order=order)
        details_1 = []
        for item in order_items:
            # products.append(item.product)
            detail = Detail(
                product_name=item.product_name,
                image=item.product.image,
                item_price=item.price,
                quantity=item.quantity,
                price=item.price*item.quantity,
                shop_name=item.shop_name,
            )

            details_1.append(detail)
        order_info = OrderInfo(order_id=order.id, order_number=order.order_number, total_price=order.total_price, status=order.status, payment_method=order.payment_method,
                               created_at=order.created_at,paid_at=order.paid_at, details=details_1)
        print(len(details_1))
        order_infos.append(order_info)
        print(len(order_infos))
    order_number = request.GET.get('q')
    filtered_order_infos = []

    if order_number:
        filtered_order_infos = [
            order_info for order_info in order_infos
            if str(order_info.order_id) == order_number
        ]
    else:
        filtered_order_infos = order_infos
    return render(request, "history_orders.html", {'id': id, 'orders': filtered_order_infos})


def order_detail(request, id):
    # id获取order
    order = Order.objects.get(id=id)

    class OrderInfo:
        def __init__(self, order_id, order_number, total_price, status, payment_method, created_at, paid_at,address):
            self.order_id = order_id
            self.order_number = order_number
            self.total_price = total_price
            self.status = status
            self.payment_method = payment_method
            self.created_at = created_at
            self.paid_at = paid_at
            self.address = address

    address_1 = Address.objects.get(order.shopping_address)
    order_info = OrderInfo(order_id=order.id, order_number=order.order_number, total_price=order.total_price,
                           status=order.status, payment_method=order.payment_method,
                           created_at=order.created_at, paid_at=order.paid_at, address=address_1)

    class Final_detail:
        def __init__(self, product_name, image, item_price, quantity, description, total_price):
            self.product_name = product_name
            self.image = image
            self.item_price = item_price
            self.item_quantity = quantity
            self.description = description
            self.total_price = total_price


    class Final_result:
        def __init__(self, merchant, final_details):
            self.merchant = merchant
            self.final_details = final_details

    order_items = OrderItem.objects.filter(order=order)  # 获取所有订单项
    products = []
    # 获得所有商品
    for order_item in order_items:
        product = order_item.product
        products.append(product)
    # 获得所有店家
    sellers = []
    for product in products:
        seller = product.seller
        sellers.append(seller)

    final_results = []
    sellers = list({product_1.seller.id: product_1.seller for product_1 in products}.values())
    for seller in sellers:
        final_details = []
        for product in products:
            if product.seller_id == seller.id:
                name = product.name
                picture = product.image
                description = product.description
                order_item = OrderItem.objects.get(product_id=product.id)
                unit_price = product.price
                quantity = order_item.quantity
                total_price = order_item.price *order_item.quantity#product_name, image, item_price, quantity, price,description,total_price)
                final_detail = Final_detail(name, picture, unit_price, quantity, description, total_price)
                final_details.append(final_detail)
        final_result = Final_result(seller, final_details)
        final_results.append(final_result)

    return render(request, 'order_detail.html', {'order_info': order_info, 'final_results': final_results})


