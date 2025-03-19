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


<<<<<<< HEAD
@csrf_exempt
def list_orders(request):
    """ 获取所有订单 """
    if request.method == "GET":
        orders = Order.objects.all().values("id", "order_number", "total_price", "status", "created_at")

        return JsonResponse(list(orders), safe=False, json_dumps_params={'ensure_ascii': False},
                            content_type="application/json; charset=utf-8")

    return JsonResponse({"message": "仅支持 GET 请求"}, status=400, json_dumps_params={'ensure_ascii': False},
                        content_type="application/json; charset=utf-8")


@csrf_exempt
def order_detail(request, order_number):
    """ 获取单个订单详情 """
    try:
        order = Order.objects.get(order_number=order_number)
        return JsonResponse(
            {"order_number": order.order_number, "total_price": order.total_price, "status": order.status},
            json_dumps_params={'ensure_ascii': False},
            content_type="application/json; charset=utf-8"
        )
    except Order.DoesNotExist:
        return JsonResponse({"message": "订单不存在"}, status=404, json_dumps_params={'ensure_ascii': False},
                            content_type="application/json; charset=utf-8")

@csrf_exempt
def pay_order(request, order_number):
    """ 支付订单 """
    if request.method == "POST":
        try:
            order = Order.objects.get(order_number=order_number)
            if order.status != "pending":
                return JsonResponse({"message": "订单无法支付（当前状态: " + order.status + "）"}, status=400, json_dumps_params={'ensure_ascii': False})

            # 模拟支付成功
            order.status = "paid"
            order.save()

            return JsonResponse(
                {"message": "订单支付成功", "order_number": order.order_number, "status": order.status},
                json_dumps_params={'ensure_ascii': False},
                content_type="application/json; charset=utf-8"
            )
        except Order.DoesNotExist:
            return JsonResponse({"message": "订单不存在"}, status=404, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=utf-8")

    return JsonResponse({"message": "仅支持 POST 请求"}, status=400, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=utf-8")


@csrf_exempt
def update_order(request, order_number):
    """ 更新订单状态 """
    if request.method == "POST":
        try:
            order = Order.objects.get(order_number=order_number)
            data = json.loads(request.body)
            new_status = data.get("status", order.status)
            order.status = new_status
            order.save()
            return JsonResponse(
                {"message": "订单状态更新成功", "order_number": order.order_number, "status": order.status},
                json_dumps_params={'ensure_ascii': False},
                content_type="application/json; charset=utf-8"
            )
        except Order.DoesNotExist:
            return JsonResponse({"message": "订单不存在"}, status=404, json_dumps_params={'ensure_ascii': False},
                                content_type="application/json; charset=utf-8")

    return JsonResponse({"message": "仅支持 POST 请求"}, status=400, json_dumps_params={'ensure_ascii': False},
                        content_type="application/json; charset=utf-8")


@csrf_exempt
def delete_order(request, order_number):
    """ 删除订单 """
    if request.method == "DELETE":
        try:
            order = Order.objects.get(order_number=order_number)
            order.delete()
            return JsonResponse({"message": "订单删除成功"}, json_dumps_params={'ensure_ascii': False},
                                content_type="application/json; charset=utf-8")
        except Order.DoesNotExist:
            return JsonResponse({"message": "订单不存在"}, status=404, json_dumps_params={'ensure_ascii': False},
                                content_type="application/json; charset=utf-8")

    return JsonResponse({"message": "仅支持 DELETE 请求"}, status=400, json_dumps_params={'ensure_ascii': False},
                        content_type="application/json; charset=utf-8")
=======
@login_required
def confirm_receipt(request, order_id):
    """确认收货，订单状态改为完成"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'shipped':
        order.status = 'completed'
        order.save()
        return JsonResponse({'status': 'success', 'message': 'Order marked as completed.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid order status.'}, status=400)
>>>>>>> origin/feature-orders
