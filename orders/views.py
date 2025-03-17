from itertools import product

from django.shortcuts import render
from orders.models import Order, Payment, Order_Item, Product


# Create your views here.
def history_order(request, id):
    orders = Order.objects.filter(consumer_id=id)
    order_infos = []

    class Detail:
        def __init__(self, shop_name, product_name, image, item_price, item_quantity, unit_price,price):
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
       # products = []  # 用列表存储 Product 对象

        order_items = Order_Item.objects.filter(order=order)
        details_1 = []
        print(len(details_1))
        for item in order_items:
            #products.append(item.product)  # 直接用外键访问 product
            detail = Detail(
                shop_name=item.product.merchant.shop_name,  # 假设 Product 关联 Shop
                product_name=item.product.name,
                image=item.product.image,
                item_price=item.price,
                item_quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )

            details_1.append(detail)
        order_info = OrderInfo(order_id=order.id, order_time=order.order_time, order_status=order.order_state,
                               total_price=order.total_price, paid_status=payment.paid_status, details=details_1)
        order_infos.append(order_info)
        print(len(order_infos))
    return render(request, "history_orders.html", {'id': id, 'orders': order_infos})
