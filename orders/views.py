# orders/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.crypto import get_random_string
from .models import Order, OrderItem
from cart.models import Cart, CartItem


@login_required
def order_list(request):
    """显示当前用户的所有订单"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """查看订单详情"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def create_order(request):
    """从购物车创建订单"""
    cart = get_object_or_404(Cart, user=request.user)
    if cart.items.count() == 0:
        return redirect('cart:cart_detail')

    order_number = get_random_string(12).upper()
    order = Order.objects.create(
        user=request.user,
        order_number=order_number,
        total_price=cart.get_total_price(),
        shipping_address=request.session.get('shipping_info', {}).get('address', '')
    )

    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product_name=item.product_name,
            price=item.product_price,
            quantity=item.quantity
        )

    cart.items.all().delete()
    return redirect('orders:order_detail', order_id=order.id)


@login_required
def confirm_receipt(request, order_id):
    """确认收货，订单状态改为完成"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'shipped':
        order.status = 'completed'
        order.save()
        return JsonResponse({'status': 'success', 'message': 'Order marked as completed.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid order status.'}, status=400)
