# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import uuid
import json

from .models import Cart, CartItem
from products.models import Product,  ProductVariant
from orders.models import Order, OrderItem
from .forms import ShippingAddressForm

def get_cart(request):
    """Helper function to get or create a cart for the current user."""
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        return cart
    return None

@login_required
def cart_detail(request):
    """Display all items in the user's cart, grouped by shop/merchant.
    cart = get_cart(request)
    if not cart:
        return redirect('users:login')
    
    # Group cart items by category (as a stand-in for shop)
    cart_items = cart.items.select_related('product').all()
    
    # Group by category
    shops_items = {}
    for item in cart_items:
        category_name = item.product.category.name
        if category_name not in shops_items:
            shops_items[category_name] = []
        shops_items[category_name].append(item)
    
    context = {
        'cart': cart,
        'shops_items': shops_items,
        'total_price': cart.get_total_price(),
    }
    return render(request, 'cart/cart.html', context)
    """
    cart = get_cart(request)
    if not cart:
        return redirect('users:login')
    
    # 获取购物车项目
    cart_items = cart.items.all()
    
    # 按类别分组 (模拟按商店分组)
    # 由于我们没有真正的商店信息，我们可以假设每个产品ID的第一个数字是商店ID
    shops_items = {}
    for item in cart_items:
        shop_id = f"Shop {item.product_id_test % 3 + 1}"  # productid注意！
        if shop_id not in shops_items:
            shops_items[shop_id] = []
        shops_items[shop_id].append(item)
    
    context = {
        'cart': cart,
        'shops_items': shops_items,
        'total_price': sum(item.get_price() for item in cart_items),
    }
    return render(request, 'cart/cart.html', context)
    

@login_required
@require_POST
def cart_add(request, product_id):
    """Add a product to the cart.
    cart = get_cart(request)
    product = get_object_or_404(Product, id=product_id)
    
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': 1}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': f"{product.name} has been added to your cart.",
            'cart_total': cart.get_total_items()
        })
    
    return redirect('products:product_list')
    """
    cart = get_cart(request)
    if not cart:
        return redirect('users:login')

    # json request to get variant product id
    variant_id = None
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            variant_id = data.get('variant_id')
        except json.JSONDecodeError:
            pass

    product = get_object_or_404(Product, id=product_id)
    variant = None

    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
        price = variant.price
        stock = variant.stock
    else:
        price = product.price
        stock = product.stock

    # check stock
    if stock <= 0:
        return JsonResponse({
            "status": "error",
            "message": "商品已售罄"
        })

    try:
        # compile old version
        if hasattr(product, 'id') and product.id:
            if variant:
                cart_item = CartItem.objects.filter(
                    cart=cart,
                    product=product,
                    variant=variant
                ).first()
            else:
                cart_item = CartItem.objects.filter(
                    cart=cart,
                    product=product,
                    variant__isnull=True
                ).first()
        else:
            cart_item = CartItem.objects.filter(
                cart=cart,
                product_id_test=product_id
            ).first()

        if cart_item:
            if cart_item.quantity + 1 <= stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                return JsonResponse({
                    "status": "error",
                    "message": "understock"
                })
        else:
            if hasattr(product, 'id') and product.id:
                CartItem.objects.create(
                    cart=cart,
                    product=product,
                    variant=variant,
                    product_name=product.name,
                    product_price=price,
                    product_image=product.image.url if product.image else None,
                    quantity=1
                )
            else:
                CartItem.objects.create(
                    cart=cart,
                    product_id_test=product_id,
                    product_name=product["name"],
                    product_price=product["price"],
                    product_image=product["image"],
                    quantity=1
                )

    except Exception as e:
        print(f"Error adding item to cart: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

    return JsonResponse({
        "status": "success",
        "message": f"{'变体商品' if variant else '商品'} 已添加到购物车",
        "cart_total": cart.items.count()
    })

@login_required
def cart_remove(request, item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        cart = get_cart(request)
        return JsonResponse({
            'status': 'success',
            'message': "Item removed from cart.",
            'cart_total': cart.get_total_items(),
            'cart_price': float(cart.get_total_price())
        })
    
    return redirect('cart:cart_detail')

@login_required
def cart_update(request, item_id):
    """Update the quantity of an item in the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)

    if request.method == 'POST':
        if request.content_type == 'application/json':
            try:
                data = json.loads(request.body)
                change = data.get('change', 0)

                new_quantity = cart_item.quantity + change

                if new_quantity <= 0:
                    cart_item.delete()
                    cart = get_cart(request)
                    return JsonResponse({
                        'status': 'success',
                        'message': 'The item has been removed from the cart.',
                        'cart_total': cart.get_total_items(),
                        'cart_price': float(cart.get_total_price())
                    })

                stock = 0

                if cart_item.variant:
                    stock = cart_item.variant.stock
                elif cart_item.product:
                    stock = cart_item.product.stock
                else:
                    stock = 999

                if new_quantity > stock:
                    return JsonResponse({
                        'status': 'error',
                        'message': 'understock'
                    })

                cart_item.quantity = new_quantity
                cart_item.save()

                cart = get_cart(request)
                return JsonResponse({
                    'status': 'success',
                    'item_price': float(cart_item.get_price()),
                    'cart_total': cart.get_total_items(),
                    'cart_price': float(cart.get_total_price())
                })

            except json.JSONDecodeError:
                pass

        else:
            quantity = int(request.POST.get('quantity', 1))

            if quantity < 1:
                cart_item.delete()
            else:
                stock = 0

                if cart_item.variant:
                    stock = cart_item.variant.stock
                elif cart_item.product:
                    stock = cart_item.product.stock
                else:
                    stock = 999

                if quantity <= stock:
                    cart_item.quantity = quantity
                    cart_item.save()

            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                cart = get_cart(request)
                return JsonResponse({
                    'status': 'success',
                    'item_price': float(cart_item.get_price()),
                    'cart_total': cart.get_total_items(),
                    'cart_price': float(cart.get_total_price())
                })

    return redirect('cart:cart_detail')

@login_required
def cart_search(request):

    # #Search for items in the cart.
    # query = request.GET.get('q', '')
    # cart = get_cart(request)
    
    # if query:
        # items = cart.items.filter(
            # Q(product__name__icontains=query) | 
            # Q(product__description__icontains=query)
        # ).select_related('product')
    # else:
        # items = cart.items.all().select_related('product')
    
    # items_data = []
    # for item in items:
        # items_data.append({
            # 'id': item.id,
            # 'product_id': item.product.id,
            # 'name': item.product.name,
            # 'price': float(item.product.price),
            # 'quantity': item.quantity,
            # 'total_price': float(item.get_price()),
            # 'image': item.product.image.url if item.product.image else None,
        # })
    
    # return JsonResponse({'items': items_data})

    query = request.GET.get('q', '')
    cart = get_cart(request)
    
    if query:
        items = cart.items.filter(
            Q(product_name__icontains=query)  # 使用product_name而不是product__name
        )
    else:
        items = cart.items.all()
    
    items_data = []
    for item in items:
        items_data.append({
            'id': item.id,
            'product_id': item.product_id_test,  # 使用正确的字段
            'name': item.product_name,
            'price': float(item.product_price),
            'quantity': item.quantity,
            'total_price': float(item.get_price()),
            'image': item.product_image,
        })
    
    return JsonResponse({'items': items_data})

@login_required
def checkout(request):

    # 修改
    # #Display checkout page with cart summary.
    # cart = get_cart(request)
    # if not cart or cart.items.count() == 0:
        # return redirect('products:product_list')
    
    # context = {
        # 'cart': cart,
        # 'cart_items': cart.items.select_related('product').all(),
        # 'total_price': cart.get_total_price(),
    # }
    # return render(request, 'cart/checkout.html', context)

    cart = get_cart(request)
    if not cart or cart.items.count() == 0:
        return redirect('products:product_list')
    
    context = {
        'cart': cart,
        'cart_items': cart.items.all(),  # 删除select_related('product')
        'total_price': cart.get_total_price(),
    }
    return render(request, 'cart/checkout.html', context)

@login_required
def shipping(request):
    """Handle shipping address information."""
    cart = get_cart(request)
    if not cart or cart.items.count() == 0:
        return redirect('products:product_list')
    
    if request.method == 'POST':
        form = ShippingAddressForm(request.POST)
        if form.is_valid():
            # Store shipping info in session
            request.session['shipping_info'] = {
                'name': form.cleaned_data['name'],
                'phone': form.cleaned_data['phone'],
                'address': form.cleaned_data['address'],
                'postal_code': form.cleaned_data['postal_code'],
            }
            return redirect('cart:payment')
    else:
        form = ShippingAddressForm()
    
    context = {
        'form': form,
        'cart': cart,
        'total_price': cart.get_total_price(),
    }
    return render(request, 'cart/shipping.html', context)

@login_required
def payment(request):
    """Handle payment process with QR code."""
    cart = get_cart(request)
    if not cart or cart.items.count() == 0:
        return redirect('products:product_list')
    
    shipping_info = request.session.get('shipping_info', {})
    if not shipping_info:
        return redirect('cart:shipping')
    
    # Generate order number for QR code
    order_number = str(uuid.uuid4()).replace("-", "")[:12]
    request.session['pending_order_number'] = order_number
    
    context = {
        'cart': cart,
        'total_price': cart.get_total_price(),
        'shipping_info': shipping_info,
        'order_number': order_number,
    }
    return render(request, 'cart/payment.html', context)

@login_required
def payment_success(request):

    #Process successful payment and create order.
    cart = get_cart(request)
    if not cart or cart.items.count() == 0:
        return redirect('products:product_list')

    shipping_info = request.session.get('shipping_info', {})
    order_number = request.session.get('pending_order_number')

    if not shipping_info or not order_number:
        return redirect('cart:checkout')
    
    # Create the order
    order = Order.objects.create(
        user=request.user,
        order_number=order_number,
        total_price=cart.get_total_price(),
        status='paid',
        shipping_address=shipping_info.get('address', ''),
    )
    
    # Create order items
    for cart_item in cart.items.all():
        product_name = cart_item.product_name
        if not product_name and cart_item.product:
            product_name = cart_item.product.name

        price = cart_item.product_price
        if price is None and cart_item.variant:
            price = cart_item.variant.price
        elif price is None and cart_item.product:
            price = cart_item.product.price

        OrderItem.objects.create(
            order=order,
            product_name=product_name,
            quantity=cart_item.quantity,
            price=price,
        )

        if cart_item.variant:
            cart_item.variant.reduce_stock(cart_item.quantity)
        elif cart_item.product:
            cart_item.product.reduce_stock(cart_item.quantity)
    
    # Clear the cart
    cart.items.all().delete()
    
    # Clear session data
    if 'shipping_info' in request.session:
        del request.session['shipping_info']
    if 'pending_order_number' in request.session:
        del request.session['pending_order_number']
    
    return render(request, 'cart/payment_success.html', {'order': order})
