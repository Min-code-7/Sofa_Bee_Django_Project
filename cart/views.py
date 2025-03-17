# cart/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db.models import Q
import uuid

from .models import Cart, CartItem
from products.models import Product
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
    
    # 获取产品 (使用测试数据)
    from products.views import PRODUCTS
    product = None
    for p in PRODUCTS:
        if p["id"] == product_id:
            product = p
            break
    
    if not product:
        return JsonResponse({"status": "error", "message": "Product not found"}, status=404)
    
    # 模拟添加到购物车
    return JsonResponse({
        "status": "success",
        "message": f"{product['name']} has been added to your cart.",
        "cart_total": 1  # 简化逻辑
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
    if request.method == 'POST':
        cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity < 1:
            cart_item.delete()
        else:
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
    """Search for items in the cart."""
    query = request.GET.get('q', '')
    cart = get_cart(request)
    
    if query:
        items = cart.items.filter(
            Q(product__name__icontains=query) | 
            Q(product__description__icontains=query)
        ).select_related('product')
    else:
        items = cart.items.all().select_related('product')
    
    items_data = []
    for item in items:
        items_data.append({
            'id': item.id,
            'product_id': item.product.id,
            'name': item.product.name,
            'price': float(item.product.price),
            'quantity': item.quantity,
            'total_price': float(item.get_price()),
            'image': item.product.image.url if item.product.image else None,
        })
    
    return JsonResponse({'items': items_data})

@login_required
def checkout(request):
    """Display checkout page with cart summary."""
    cart = get_cart(request)
    if not cart or cart.items.count() == 0:
        return redirect('products:product_list')
    
    context = {
        'cart': cart,
        'cart_items': cart.items.select_related('product').all(),
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
    """Process successful payment and create order."""
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
        OrderItem.objects.create(
            order=order,
            product_name=cart_item.product.name,
            quantity=cart_item.quantity,
            price=cart_item.product.price,
        )
    
    # Clear the cart
    cart.items.all().delete()
    
    # Clear session data
    if 'shipping_info' in request.session:
        del request.session['shipping_info']
    if 'pending_order_number' in request.session:
        del request.session['pending_order_number']
    
    return render(request, 'cart/payment_success.html', {'order': order})
