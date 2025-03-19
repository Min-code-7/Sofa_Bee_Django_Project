import string
import random
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http.response import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail

from addresses.models import Address
from orders.models import OrderItem, Order
from profiles.models import CaptchaModel
from users.models import UserProfile


# Create your views here.
def profiles(request, id=None):
    if id is None:
        id = request.user.id
    
    try:
        # 尝试获取用户资料
        userProfile = UserProfile.objects.get(user_id=id)
        
        # 如果是普通用户
        if userProfile.user_type == "regular" or userProfile.user_type == "normal user":
            addresses = Address.objects.filter(user=request.user)
            return render(request, 'profile.html', {'user': userProfile.user, 'addresses': addresses})

        # 如果是商家用户
        addresses = Address.objects.filter(user=request.user, is_default=True)
        return render(request, 'merchant_profile.html', {'user': userProfile.user, 'addresses': addresses})
    
    except UserProfile.DoesNotExist:
        # 如果用户资料不存在，创建一个新的
        if request.user.is_authenticated:
            # 为当前登录用户创建资料
            userProfile = UserProfile.objects.create(
                user=request.user,
                user_type='regular'  # 默认为普通用户
            )
            addresses = []
            return render(request, 'profile.html', {'user': request.user, 'addresses': addresses})
        else:
            # 如果用户未登录，重定向到登录页面
            from django.shortcuts import redirect
            return redirect('users:login')


def modify(request):
    id = request.user.id
    user = request.user
    if request.method == 'POST':
        username = request.POST.get('name')
        if username is None:
            username = user.username
        email = request.POST.get('email')
        if request.POST.get('new-email'):
            email = request.POST.get('new-email')
        phone = request.POST.get('phone')
        
        # 更新用户信息
        user.username = username
        user.email = email
        
        # 处理密码修改
        current_password = request.POST.get('current-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')
        
        if current_password and new_password and confirm_password:
            # 验证当前密码
            if user.check_password(current_password):
                # 验证新密码和确认密码是否匹配
                if new_password == confirm_password:
                    user.set_password(new_password)
                    messages.success(request, "Password updated successfully.")
                else:
                    messages.error(request, "New password and confirmation do not match.")
            else:
                messages.error(request, "Current password is incorrect.")
        
        user.save()
        
        # 更新用户资料中的电话号码
        if phone:
            try:
                userprofile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                # 如果用户资料不存在，创建一个新的
                userprofile = UserProfile.objects.create(
                    user=user,
                    user_type='regular'  # 默认为普通用户
                )
            
            userprofile.phone_number = phone
            userprofile.save()

        # 修改重定向，确保传递用户ID
        return redirect('profiles', id=user.id)

    return render(request, 'modify.html', {'user': user})


def send_email_captcha(request):
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


def history_order(request, id=None):
    if id is None:
        id = request.user.id
    orders = Order.objects.filter(user_id=id).order_by('-created_at')  # 按创建时间倒序排列

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

    try:
        for order in orders:
            try:
                order_items = OrderItem.objects.filter(order=order)
                details_1 = []
                for item in order_items:
                    try:
                        # 尝试获取订单项详情
                        image = None
                        try:
                            # 通过product_name查找对应的Product对象
                            from products.models import Product
                            product = Product.objects.filter(name=item.product_name).first()
                            if product and product.image:
                                image = product.image.url
                        except Exception:
                            # 如果获取图片失败，使用None
                            pass
                            
                        # 获取商品的卖家信息
                        shop_name = ''
                        try:
                            from products.models import Product
                            product = Product.objects.filter(name=item.product_name).first()
                            if product and product.seller:
                                shop_name = product.seller.username
                        except Exception:
                            # 如果获取卖家信息失败，使用空字符串
                            pass
                            
                        detail = Detail(
                            product_name=item.product_name,
                            image=image,
                            item_price=item.price,
                            quantity=item.quantity,
                            price=item.price*item.quantity,
                            shop_name=shop_name,
                        )
                        details_1.append(detail)
                    except Exception:
                        # 如果处理订单项时出错，跳过
                        continue
                        
                # 只有当有订单项详情时才添加订单信息
                if details_1:
                    order_info = OrderInfo(
                        order_id=order.id, 
                        order_number=order.order_number, 
                        total_price=order.total_price, 
                        status=order.status, 
                        payment_method=order.payment_method,
                        created_at=order.created_at, 
                        paid_at=order.paid_at, 
                        details=details_1
                    )
                    order_infos.append(order_info)
            except Exception:
                # 如果处理订单时出错，跳过
                continue
    except Exception as e:
        # 如果处理订单列表时出错，显示错误消息
        messages.error(request, f"获取订单历史时出错: {str(e)}")
        
    order_number = request.GET.get('q')
    filtered_order_infos = []

    if order_number:
        filtered_order_infos = [
            order_info for order_info in order_infos
            if str(order_info.order_number) == order_number
        ]
    else:
        filtered_order_infos = order_infos
    return render(request, "history_orders.html", {'id': id, 'orders': filtered_order_infos})


def delete_order(request, id):
    """删除订单"""
    try:
        order = Order.objects.get(id=id, user=request.user)
        order.delete()
        messages.success(request, "订单已成功删除")
    except Order.DoesNotExist:
        messages.error(request, "订单不存在或您无权删除此订单")
    
    return redirect('history_order')


def order_detail(request, id):
    try:
        # 尝试获取订单
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        # 如果订单不存在，重定向到订单历史页面
        messages.error(request, "订单不存在")
        return redirect('history_order')

    class OrderInfo:
        def __init__(self, order_id, order_number, total_price, status, payment_method, created_at, paid_at, address):
            self.order_id = order_id
            self.order_number = order_number
            self.total_price = total_price
            self.status = status
            self.payment_method = payment_method
            self.created_at = created_at
            self.paid_at = paid_at
            self.address = address

    # 修复地址获取逻辑
    try:
        # 尝试将shipping_address解析为地址ID
        address_id = int(order.shipping_address)
        address_1 = Address.objects.get(id=address_id)
    except (ValueError, Address.DoesNotExist):
        # 如果无法解析为ID或地址不存在，则使用字符串表示
        address_1 = order.shipping_address
    
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
    
    # 通过product_name查找对应的Product对象
    from products.models import Product
    products = []
    for order_item in order_items:
        try:
            product = Product.objects.filter(name=order_item.product_name).first()
            if product:
                products.append(product)
        except Exception:
            # 如果产品不存在或有其他问题，跳过这个订单项
            continue
    
    # 如果没有有效的产品，显示空结果
    if not products:
        return render(request, 'order_detail.html', {
            'order_info': order_info, 
            'final_results': [],
            'error_message': '此订单没有有效的产品信息'
        })
    
    # 获得所有店家
    sellers = []
    for product in products:
        try:
            if product.seller:
                sellers.append(product.seller)
        except Exception:
            # 如果卖家不存在，跳过
            continue

    final_results = []
    try:
        # 尝试获取所有卖家
        sellers = list({product_1.seller.id: product_1.seller for product_1 in products if product_1.seller}.values())
        
        for seller in sellers:
            final_details = []
            for product in products:
                try:
                    if product.seller_id == seller.id:
                        name = product.name
                        picture = product.image
                        description = product.description
                        
                        try:
                            # 尝试获取订单项
                            order_item = OrderItem.objects.filter(order=order, product_name=product.name).first()
                            if order_item:
                                unit_price = product.price
                                quantity = order_item.quantity
                                total_price = order_item.price * order_item.quantity
                                
                                final_detail = Final_detail(name, picture, unit_price, quantity, description, total_price)
                                final_details.append(final_detail)
                        except Exception:
                            # 如果订单项不存在，跳过
                            continue
                except Exception:
                    # 如果处理产品时出错，跳过
                    continue
                    
            if final_details:  # 只有当有详情时才添加结果
                final_result = Final_result(seller, final_details)
                final_results.append(final_result)
    except Exception as e:
        # 如果处理卖家时出错，显示错误消息
        return render(request, 'order_detail.html', {
            'order_info': order_info, 
            'final_results': [],
            'error_message': f'处理订单详情时出错: {str(e)}'
        })

    return render(request, 'order_detail.html', {'order_info': order_info, 'final_results': final_results})
