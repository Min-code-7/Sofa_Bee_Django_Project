# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import uuid
from django.contrib import messages
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
    """Display all items in the user's cart, grouped by shop/merchant."""
    cart = get_cart(request)
    if not cart:
        return redirect('users:login')
    
    # Get cart items without using select_related to avoid the product_id issue
    cart_items = cart.items.all()
    
    # Handle search query
    query = request.GET.get('q', '')
    if query and False:  # 暂时禁用搜索功能
        cart_items = cart_items.filter(
            Q(product__name__icontains=query) |
            Q(product__description__icontains=query)
        )
    
    # Group by seller (shop) - 简化处理，不再按卖家分组
    shops_items = {"All Items": []}
    for item in cart_items:
        shops_items["All Items"].append(item)
    
    context = {
        'cart': cart,
        'shops_items': shops_items,
        'total_price': cart.get_total_price(),
    }
    return render(request, 'cart/cart.html', context)
    

@login_required
@require_POST
def cart_add(request, product_id):
    """ 
    Add a product to the cart.
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
    """
    cart = get_cart(request)
    if not cart:
        return redirect('users:login')
    
    # Get product from database
    product = get_object_or_404(Product, id=product_id)
    
    # Check stock
    if product.stock <= 0:
        return JsonResponse({
            "status": "error",
            "message": "Sorry, this product is out of stock."
        })
    
    try:
        # 不使用get_or_create，而是先查询，如果不存在则创建
        cart_item = CartItem.objects.filter(cart=cart, product_id_test=product_id).first()
        
        if cart_item:
            created = False
        else:
            created = True
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,  # 设置product字段
                product_id_test=product_id,
                product_name=product.name,
                product_price=product.price,
                product_image=product.image.url if product.image else None,
                quantity=1
            )
        
        if not created:
            # If exists, increase quantity
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"Sorry, only {product.stock} items available in stock."
                })
    
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    return JsonResponse({
        "status": "success",
        "message": f"{product.name} has been added to your cart.",
        "cart_total": cart.items.count()
    })

@login_required
def cart_remove(request, item_id):
    """Remove an item from the cart."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    
    
    cart = get_cart(request)
    return JsonResponse({
        'status': 'success',
        'message': "Item removed from cart.",
        'cart_total': cart.get_total_items(),
        'cart_price': float(cart.get_total_price())
    })
    
    # return redirect('cart:cart_detail')
    """ try:
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        cart_item.delete()
        
        cart = get_cart(request)
        
        return JsonResponse({
            'status': 'success',
            'message': "Item has been removed from cart",
            'cart_total': cart.items.count(),
            'cart_price': float(cart.get_total_price())
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f"Delete failed: {str(e)}"
        }, status=500) """

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
    query = request.GET.get('q', '')
    cart = get_cart(request)
    
    # 简化搜索，暂时不使用过滤
    items = cart.items.all()
    
    items_data = []
    for item in items:
        # 使用product_name和product_price字段，如果存在的话
        name = item.product_name if hasattr(item, 'product_name') and item.product_name else "Product"
        price = float(item.product_price) if hasattr(item, 'product_price') and item.product_price else 0
        image = item.product_image if hasattr(item, 'product_image') and item.product_image else None
        
        # 如果有product关系，则使用product的属性作为备选
        if hasattr(item, 'product') and item.product:
            if not name:
                name = item.product.name
            if not price:
                price = float(item.product.price)
            if not image and item.product.image:
                image = item.product.image.url
        
        items_data.append({
            'id': item.id,
            'product_id': getattr(item, 'product_id_test', 0),
            'name': name,
            'price': price,
            'quantity': item.quantity,
            'total_price': float(item.get_price()),
            'image': image,
        })
    
    return JsonResponse({'items': items_data})

@login_required
def checkout(request):

    # Modified
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
    
    # 获取所有购物车商品
    cart_items = cart.items.all()
    
    # 检查库存 - 简化处理，暂时跳过库存检查
    # out_of_stock_items = []
    # for item in cart_items:
    #     if item.product and item.quantity > item.product.stock:
    #         out_of_stock_items.append({
    #             'name': item.product.name,
    #             'available': item.product.stock,
    #             'requested': item.quantity
    #         })
    
    # if out_of_stock_items:
    #     context = {
    #         'out_of_stock_items': out_of_stock_items
    #     }
    #     return render(request, 'cart/stock_error.html', context)
    
    # 调试信息
    for item in cart_items:
        product_name = item.product_name if hasattr(item, 'product_name') and item.product_name else "Unknown"
        product_price = item.product_price if hasattr(item, 'product_price') and item.product_price else 0
        print(f"DEBUG: Product Name = {product_name}, Price = {product_price}, Quantity = {item.quantity}")

    context = {
        'cart': cart,
        'cart_items': cart_items,
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
        form = ShippingAddressForm(request.POST, user=request.user)
        if form.is_valid():
            # Check if user selected an existing address
            existing_address = form.cleaned_data.get('use_existing_address')
            
            if existing_address:
                # Use the selected address
                request.session['shipping_info'] = {
                    'name': existing_address.receiver_name,
                    'phone': existing_address.receiver_phone,
                    'address': f"{existing_address.province} {existing_address.city} {existing_address.district}".strip(),
                    'postal_code': existing_address.detail_address,  # detail_address is used for postal code
                }
            else:
                # Use the form data
                request.session['shipping_info'] = {
                    'name': form.cleaned_data['name'],
                    'phone': form.cleaned_data['phone'],
                    'address': form.cleaned_data['address'],
                    'postal_code': form.cleaned_data['postal_code'],
                }
                
                # Save address to profile if requested
                if form.cleaned_data.get('save_address'):
                    from addresses.models import Address
                    
                    # Create a new address
                    Address.objects.create(
                        user=request.user,
                        receiver_name=form.cleaned_data['name'],
                        receiver_phone=form.cleaned_data['phone'],
                        province='',  # Not using separate province/city/district
                        city='',
                        district='',
                        detail_address=form.cleaned_data['postal_code'],  # Store postal code in detail_address
                        is_default=False  # Not setting as default
                    )
                    
            return redirect('cart:payment')
    else:
        form = ShippingAddressForm(user=request.user)
    
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
    
     # Check stock again - 简化处理，暂时跳过库存检查
    # for item in cart.items.all():
    #     if item.product and item.quantity > item.product.stock:
    #         product_name = item.product_name if hasattr(item, 'product_name') and item.product_name else item.product.name
    #         messages.error(request, f"Sorry, '{product_name}' now only has {item.product.stock} items in stock.")
    #         return redirect('cart:cart_detail')
        
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
    
    # Final stock check and reduce inventory - 简化处理，暂时跳过库存检查
    # for item in cart.items.all():
    #     if item.product and item.quantity > item.product.stock:
    #         product_name = item.product_name if hasattr(item, 'product_name') and item.product_name else item.product.name
    #         messages.error(request, f"Sorry, '{product_name}' is now out of stock.")
    #         return redirect('cart:cart_detail')
    #     
    #     # Reduce stock
    #     if item.product:
    #         item.product.reduce_stock(item.quantity)

    # Create the order with properly formatted address
    name = shipping_info.get('name', '')
    phone = shipping_info.get('phone', '')
    address = shipping_info.get('address', '')
    postal_code = shipping_info.get('postal_code', '')
    
    # Format address and postal code with comma if both exist
    delivery_address = address
    if postal_code:
        delivery_address = f"{address}, {postal_code}"
    
    # Create a simple formatted address string
    formatted_address = f"Full Name: {name}\nPhone Number: {phone}\nDelivery Address: {delivery_address}"
    
    order = Order.objects.create(
        user=request.user,
        order_number=order_number,
        total_price=cart.get_total_price(),
        status='paid',
        shipping_address=formatted_address,
    )
    
    # Create order items
    for cart_item in cart.items.all():
        product_name = cart_item.product_name if cart_item.product_name else "Product"
        price = cart_item.product_price if cart_item.product_price else 0

        OrderItem.objects.create(
            order=order,
            product_name=product_name,
            quantity=cart_item.quantity,
            price=price,
        )

        # 减少库存
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
