from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.contrib.auth.models import User
from .models import Order  # 确保 Order 模型已经导入


@csrf_exempt
def create_order(request):
    """ 创建订单（支持多个商品） """
    if request.method == "POST":
        data = json.loads(request.body)

        # 确保有 user
        user = User.objects.first()  # 取第一个用户

        items = data.get("items", [])
        total_price = sum(item["price"] * item["quantity"] for item in items)

        # 生成唯一订单号
        import uuid
        order_number = str(uuid.uuid4()).replace("-", "")[:12]

        # 创建订单
        order = Order.objects.create(
            user=user,
            order_number=order_number,
            total_price=total_price,
            status="pending"
        )

        return JsonResponse(
            {"message": "订单创建成功", "order_number": order.order_number},
            json_dumps_params={'ensure_ascii': False},
            content_type="application/json; charset=utf-8"
        )

    return JsonResponse({"message": "请使用 POST 请求来创建订单"}, status=400,
                        json_dumps_params={'ensure_ascii': False}, content_type="application/json; charset=utf-8")


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