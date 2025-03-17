from collections import defaultdict
from datetime import datetime
from itertools import product

from django.shortcuts import render

from addresses.models import Address
from orders.models import Order, Payment, Order_Item, Product


# Create your views here.
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