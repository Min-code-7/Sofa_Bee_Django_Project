# orders/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.crypto import get_random_string
import json
from .models import Order, OrderItem
from cart.models import Cart, CartItem


@login_required
def order_list(request):
    """Display all orders for the current user"""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'orders/order_list.html', {'orders': orders})


@login_required
def order_detail(request, order_id):
    """View order details"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def create_order(request):
    """Create an order from the shopping cart"""
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


@csrf_exempt
def list_orders(request):
    """ Get all orders """
    if request.method == "GET":
        orders = Order.objects.all().values("id", "order_number", "total_price", "status", "created_at")

        return JsonResponse(list(orders), safe=False, json_dumps_params={'ensure_ascii': False},
                            content_type="application/json; charset=utf-8")

    return JsonResponse({"message": "Only GET requests are supported"}, status=400, json_dumps_params={'ensure_ascii': False},
                        content_type="application/json; charset=utf-8")


@csrf_exempt
def order_detail(request, order_number):
    """ Get details for a single order """
    try:
        order = Order.objects.get(order_number=order_number)
        return JsonResponse(
            {"order_number": order.order_number, "total_price": order.total_price, "status": order.status},
            json_dumps_params={'ensure_ascii': False},
            content_type="application/json; charset=utf-8"
        )
    except Order.DoesNotExist:
        return JsonResponse({"message": "Order does not exist"}, status=404, json_dumps_params={'ensure_ascii': False},
                            content_type="application/json; charset=utf-8")

@csrf_exempt
def pay_order(request, order_number):
    """ Pay for an order """
    if request.method == "POST":
        try:
            order = Order.objects.get(order_number=order_number)
            if order.status != "pending":
                return JsonResponse({"message": "Order cannot be paid (current status: " + order.status + ")"}, status=400, json_dumps_params={'ensure_ascii': False})

            # Simulate successful payment
            order.status = "paid"
            order.save()

            return JsonResponse(
                {"message": "Order payment successful", "order_number": order.order_number, "status": order.status},
                json_dumps_params={'ensure_ascii': False},
                content_type="application/json; charset=utf-8"
            )
        except Order.DoesNotExist:
            return JsonResponse({"message": "Order does not exist"}, status=404, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=utf-8")

    return JsonResponse({"message": "Only POST requests are supported"}, status=400, json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=utf-8")


@csrf_exempt
def update_order(request, order_number):
    """ Update order status """
    if request.method == "POST":
        try:
            order = Order.objects.get(order_number=order_number)
            data = json.loads(request.body)
            new_status = data.get("status", order.status)
            order.status = new_status
            order.save()
            return JsonResponse(
                {"message": "Order status updated successfully", "order_number": order.order_number, "status": order.status},
                json_dumps_params={'ensure_ascii': False},
                content_type="application/json; charset=utf-8"
            )
        except Order.DoesNotExist:
            return JsonResponse({"message": "Order does not exist"}, status=404, json_dumps_params={'ensure_ascii': False},
                                content_type="application/json; charset=utf-8")

    return JsonResponse({"message": "Only POST requests are supported"}, status=400, json_dumps_params={'ensure_ascii': False},
                        content_type="application/json; charset=utf-8")


@csrf_exempt
def delete_order(request, order_number):
    """ Delete an order """
    if request.method == "DELETE":
        try:
            order = Order.objects.get(order_number=order_number)
            order.delete()
            return JsonResponse({"message": "Order deleted successfully"}, json_dumps_params={'ensure_ascii': False},
                                content_type="application/json; charset=utf-8")
        except Order.DoesNotExist:
            return JsonResponse({"message": "Order does not exist"}, status=404, json_dumps_params={'ensure_ascii': False},
                                content_type="application/json; charset=utf-8")

    return JsonResponse({"message": "Only DELETE requests are supported"}, status=400, json_dumps_params={'ensure_ascii': False},
                        content_type="application/json; charset=utf-8")
@login_required
def confirm_receipt(request, order_id):
    """Confirm receipt, change order status to completed"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    if order.status == 'shipped':
        order.status = 'completed'
        order.save()
        return JsonResponse({'status': 'success', 'message': 'Order marked as completed.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid order status.'}, status=400)
