import string
import random
import os
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
        # Try to get user profile
        userProfile = UserProfile.objects.get(user_id=id)
        
        # If regular user
        if userProfile.user_type == "regular" or userProfile.user_type == "normal user":
            addresses = Address.objects.filter(user=request.user)
            return render(request, 'profile.html', {'user': userProfile.user, 'addresses': addresses})

        # If merchant user
        addresses = Address.objects.filter(user=request.user, is_default=True)
        return render(request, 'merchant_profile.html', {'user': userProfile.user, 'addresses': addresses})
    
    except UserProfile.DoesNotExist:
        # If user profile doesn't exist, create a new one
        if request.user.is_authenticated:
            # Create profile for current logged in user
            userProfile = UserProfile.objects.create(
                user=request.user,
                user_type='regular'  # Default to regular user
            )
            addresses = []
            return render(request, 'profile.html', {'user': request.user, 'addresses': addresses})
        else:
            # If user is not logged in, redirect to login page
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
        
        # Update user information
        user.username = username
        user.email = email
        
        # Handle password change
        current_password = request.POST.get('current-password')
        new_password = request.POST.get('new-password')
        confirm_password = request.POST.get('confirm-password')
        
        if current_password and new_password and confirm_password:
            # Verify current password
            if user.check_password(current_password):
                # Verify new password and confirmation match
                if new_password == confirm_password:
                    user.set_password(new_password)
                    messages.success(request, "Password updated successfully.")
                else:
                    messages.error(request, "New password and confirmation do not match.")
            else:
                messages.error(request, "Current password is incorrect.")
        
        user.save()
        
        # Update phone number in user profile
        if phone:
            try:
                userprofile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                # If user profile doesn't exist, create a new one
                userprofile = UserProfile.objects.create(
                    user=user,
                    user_type='regular'  # Default to regular user
                )
            
            userprofile.phone_number = phone
            userprofile.save()

        # Modify redirect to ensure user ID is passed
        return redirect('profiles', id=user.id)

    return render(request, 'modify.html', {'user': user})


def send_email_captcha(request):
    # ?email=xxx
    email = request.GET.get('email')
    if not email:
        return JsonResponse({"code": 400, "message": 'Email must be provided!'})
    captcha = "".join(random.sample(string.digits, 4))
    # Store in database
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
    orders = Order.objects.filter(user_id=id).order_by('-created_at')  # Order by creation time descending

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
                        # Try to get order item details
                        image = None
                        try:
                            # Find corresponding Product object by product_name
                            from products.models import Product
                            product = Product.objects.filter(name=item.product_name).first()
                            if product and product.image:
                                image = product.image.url
                        except Exception:
                            # If getting image fails, use None
                            pass
                            
                        # Get seller information for the product
                        shop_name = ''
                        try:
                            from products.models import Product
                            product = Product.objects.filter(name=item.product_name).first()
                            if product and product.seller:
                                shop_name = product.seller.username
                        except Exception:
                            # If getting seller information fails, use empty string
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
                        # If processing order item fails, skip
                        continue
                        
                # Only add order information when there are order item details
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
                # If processing order fails, skip
                continue
    except Exception as e:
        # If processing order list fails, show error message
        messages.error(request, f"Error getting order history: {str(e)}")
        
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
    """Delete an order"""
    try:
        order = Order.objects.get(id=id, user=request.user)
        order.delete()
        messages.success(request, "Order has been successfully deleted")
    except Order.DoesNotExist:
        messages.error(request, "Order does not exist or you don't have permission to delete it")
    
    return redirect('history_order')


def change_avatar(request):
    """Change user avatar"""
    if request.method == 'POST':
        avatar = request.POST.get('avatar')
        if avatar:
            try:
                userprofile = UserProfile.objects.get(user=request.user)
                userprofile.avatar = avatar
                userprofile.save()
                messages.success(request, "Avatar updated successfully.")
            except UserProfile.DoesNotExist:
                messages.error(request, "User profile not found.")
        return redirect('profiles', id=request.user.id)
    
    # Get list of available avatars
    avatars = []
    avatars.append('default.png')  # Default avatar
    for i in range(1, 13):  # pic1.png to pic12.png
        avatars.append(f'pic{i}.png')
    
    return render(request, 'change_avatar.html', {'avatars': avatars})


def order_detail(request, id):
    try:
        # Try to get the order
        order = Order.objects.get(id=id)
    except Order.DoesNotExist:
        # If order doesn't exist, redirect to order history page
        messages.error(request, "Order does not exist")
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

    # Fix address retrieval logic
    try:
        # Try to parse shipping_address as address ID
        address_id = int(order.shipping_address)
        address_1 = Address.objects.get(id=address_id)
    except (ValueError, Address.DoesNotExist):
        # If can't parse as ID or address doesn't exist, use string representation
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

    order_items = OrderItem.objects.filter(order=order)  # Get all order items
    
    # Find corresponding Product objects by product_name
    from products.models import Product
    products = []
    for order_item in order_items:
        try:
            product = Product.objects.filter(name=order_item.product_name).first()
            if product:
                products.append(product)
        except Exception:
            # If product doesn't exist or there are other issues, skip this order item
            continue
    
    # If there are no valid products, show empty results
    if not products:
        return render(request, 'order_detail.html', {
            'order_info': order_info, 
            'final_results': [],
            'error_message': 'This order has no valid product information'
        })
    
    # Get all sellers
    sellers = []
    for product in products:
        try:
            if product.seller:
                sellers.append(product.seller)
        except Exception:
            # If seller doesn't exist, skip
            continue

    final_results = []
    try:
        # Try to get all sellers
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
                            # Try to get order item
                            order_item = OrderItem.objects.filter(order=order, product_name=product.name).first()
                            if order_item:
                                unit_price = product.price
                                quantity = order_item.quantity
                                total_price = order_item.price * order_item.quantity
                                
                                final_detail = Final_detail(name, picture, unit_price, quantity, description, total_price)
                                final_details.append(final_detail)
                        except Exception:
                            # If order item doesn't exist, skip
                            continue
                except Exception:
                    # If processing product fails, skip
                    continue
                    
            if final_details:  # Only add result when there are details
                final_result = Final_result(seller, final_details)
                final_results.append(final_result)
    except Exception as e:
        # If processing sellers fails, show error message
        return render(request, 'order_detail.html', {
            'order_info': order_info, 
            'final_results': [],
            'error_message': f'Error processing order details: {str(e)}'
        })

    return render(request, 'order_detail.html', {'order_info': order_info, 'final_results': final_results})
