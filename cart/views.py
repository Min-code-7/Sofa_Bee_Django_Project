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
    """Add a product to the cart."""
    cart = get_cart(request)
    if not cart:
        return redirect('users:login')
    
    # Get product from database
    product = get_object_or_404(Product, id=product_id)
    
    # Check for variant_id in JSON request
    variant_id = None
    variant = None
    price = product.price
    stock = product.stock
    
    if request.content_type == 'application/json':
        try:
            data = json.loads(request.body)
            variant_id = data.get('variant_id')
            if variant_id:
                variant = get_object_or_404(ProductVariant, id=variant_id, product=product)
                price = variant.price
                stock = variant.stock
        except json.JSONDecodeError:
            pass
    
    # Check stock
    if stock <= 0:
        return JsonResponse({
            "status": "error",
            "message": "Sorry, this product is out of stock."
        })
    
    try:
        # Find existing cart item with the same product and variant
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
        
        if cart_item:
            # If exists, increase quantity
            if cart_item.quantity < stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                return JsonResponse({
                    "status": "error",
                    "message": f"Sorry, only {stock} items available in stock."
                })
        else:
            # Create new cart item
            cart_item = CartItem.objects.create(
                cart=cart,
                product=product,
                variant=variant,
                product_id_test=product_id,
                product_name=product.name,
                product_price=price,
                product_image=product.image.url if product.image else None,
                quantity=1
            )
    
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
    
    variant_info = ""
    if variant:
        variant_attrs = []
        for value in variant.attribute_values.all():
            variant_attrs.append(f"{value.attribute.name}: {value.value}")
        if variant_attrs:
            variant_info = f" ({', '.join(variant_attrs)})"
    
    return JsonResponse({
        "status": "success",
        "message": f"{product.name}{variant_info} has been added to your cart.",
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
@require_POST
def update_variant(request, item_id):
    """Update the variant of a cart item."""
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    
    try:
        data = json.loads(request.body)
        product_id = data.get('product_id')
        attribute_values = data.get('attribute_values', [])
        
        if not product_id or not attribute_values:
            return JsonResponse({
                'status': 'error',
                'message': 'Missing required parameters'
            }, status=400)
        
        # Get the product
        product = get_object_or_404(Product, id=product_id)
        
        # Find the variant that matches the selected attribute values
        matching_variant = None
        for variant in product.variants.all():
            # Get all attribute value IDs for this variant
            variant_attr_values = set(value.id for value in variant.attribute_values.all())
            # Check if the selected attribute values match this variant
            if set(attribute_values) == variant_attr_values:
                matching_variant = variant
                break
        
        if not matching_variant:
            # Try to find a variant with at least some matching attributes
            best_match = None
            best_match_count = 0
            
            for variant in product.variants.all():
                variant_attr_values = set(value.id for value in variant.attribute_values.all())
                match_count = len(set(attribute_values).intersection(variant_attr_values))
                
                if match_count > best_match_count:
                    best_match = variant
                    best_match_count = match_count
            
            if best_match:
                matching_variant = best_match
            else:
                # If no match found, use the first variant
                matching_variant = product.variants.first()
        
        if not matching_variant:
            return JsonResponse({
                'status': 'error',
                'message': 'No matching variant found'
            }, status=404)
        
        # Check if the variant is in stock
        if matching_variant.stock <= 0:
            return JsonResponse({
                'status': 'error',
                'message': 'Selected variant is out of stock'
            }, status=400)
        
        # Update the cart item
        cart_item.variant = matching_variant
        cart_item.product_price = matching_variant.price
        cart_item.save()
        
        # Get variant info for the response
        variant_info = []
        for value in matching_variant.attribute_values.all():
            variant_info.append(f"{value.attribute.name}: {value.value}")
        
        return JsonResponse({
            'status': 'success',
            'message': 'Variant updated successfully',
            'variant_info': ', '.join(variant_info),
            'price': float(matching_variant.price),
            'stock': matching_variant.stock
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)

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
    cart = get_cart(request)
    if not cart or cart.items.count() == 0:
        return redirect('products:product_list')
    
    # Get selected items from form submission
    if request.method == 'POST':
        selected_item_ids = request.POST.getlist('items[]')
        
        if not selected_item_ids:
            messages.error(request, "Please select at least one item to checkout.")
            return redirect('cart:cart_detail')
        
        # Store selected item IDs in session for later use
        request.session['selected_item_ids'] = selected_item_ids
        
        # Get only the selected cart items
        cart_items = cart.items.filter(id__in=selected_item_ids)
    else:
        # If no items were selected (direct access to checkout URL)
        selected_item_ids = request.session.get('selected_item_ids', [])
        if not selected_item_ids:
            messages.error(request, "Please select items from your cart first.")
            return redirect('cart:cart_detail')
        
        cart_items = cart.items.filter(id__in=selected_item_ids)
    
    # Calculate total price of selected items
    total_price = sum(item.get_price() for item in cart_items)
    
    # Debug information
    for item in cart_items:
        product_name = item.product_name if hasattr(item, 'product_name') and item.product_name else "Unknown"
        product_price = item.product_price if hasattr(item, 'product_price') and item.product_price else 0
        print(f"DEBUG: Product Name = {product_name}, Price = {product_price}, Quantity = {item.quantity}")

    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
        'selected_item_ids': selected_item_ids,
    }
    return render(request, 'cart/checkout.html', context)

@login_required
def shipping(request):
    """Handle shipping address information."""
    cart = get_cart(request)
    if not cart or cart.items.count() == 0:
        return redirect('products:product_list')
    
    # Get selected items from session
    selected_item_ids = request.session.get('selected_item_ids', [])
    if not selected_item_ids:
        messages.error(request, "Please select items from your cart first.")
        return redirect('cart:cart_detail')
    
    # Get only the selected cart items
    cart_items = cart.items.filter(id__in=selected_item_ids)
    
    # Calculate total price of selected items
    total_price = sum(item.get_price() for item in cart_items)
    
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
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart/shipping.html', context)

@login_required
def payment(request):
    """Handle payment process with QR code."""
    cart = get_cart(request)
    if not cart or cart.items.count() == 0:
        return redirect('products:product_list')
    
    # Get selected items from session
    selected_item_ids = request.session.get('selected_item_ids', [])
    if not selected_item_ids:
        messages.error(request, "Please select items from your cart first.")
        return redirect('cart:cart_detail')
    
    # Get only the selected cart items
    cart_items = cart.items.filter(id__in=selected_item_ids)
    
    # Calculate total price of selected items
    total_price = sum(item.get_price() for item in cart_items)
    
    shipping_info = request.session.get('shipping_info', {})
    if not shipping_info:
        return redirect('cart:shipping')
    
    # Check stock for selected items
    for item in cart_items:
        stock = 0
        if item.variant:
            stock = item.variant.stock
        elif item.product:
            stock = item.product.stock
        else:
            stock = 999
            
        if item.quantity > stock:
            product_name = item.product_name if item.product_name else "Product"
            messages.error(request, f"Sorry, '{product_name}' now only has {stock} items in stock.")
            return redirect('cart:cart_detail')
        
    # Generate order number for QR code
    order_number = str(uuid.uuid4()).replace("-", "")[:12]
    request.session['pending_order_number'] = order_number
    
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'total_price': total_price,
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

    # Get selected items from session
    selected_item_ids = request.session.get('selected_item_ids', [])
    if not selected_item_ids:
        messages.error(request, "Please select items from your cart first.")
        return redirect('cart:cart_detail')
    
    # Get only the selected cart items
    cart_items = cart.items.filter(id__in=selected_item_ids)
    
    # Calculate total price of selected items
    total_price = sum(item.get_price() for item in cart_items)

    shipping_info = request.session.get('shipping_info', {})
    order_number = request.session.get('pending_order_number')

    if not shipping_info or not order_number:
        return redirect('cart:checkout')
    
    # Final stock check for selected items
    for item in cart_items:
        stock = 0
        if item.variant:
            stock = item.variant.stock
        elif item.product:
            stock = item.product.stock
        else:
            stock = 999
            
        if item.quantity > stock:
            product_name = item.product_name if item.product_name else "Product"
            messages.error(request, f"Sorry, '{product_name}' now only has {stock} items in stock.")
            return redirect('cart:cart_detail')

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
        total_price=total_price,  # Use the total price of selected items
        status='paid',
        shipping_address=formatted_address,
    )
    
    # Create order items only for selected items
    for cart_item in cart_items:
        product_name = cart_item.product_name if cart_item.product_name else "Product"
        price = cart_item.product_price if cart_item.product_price else 0

        OrderItem.objects.create(
            order=order,
            product_name=product_name,
            quantity=cart_item.quantity,
            price=price,
        )

        # Reduce stock
        if cart_item.variant:
            cart_item.variant.reduce_stock(cart_item.quantity)
        elif cart_item.product:
            cart_item.product.reduce_stock(cart_item.quantity)
    
    # Remove only the selected items from cart
    cart_items.delete()
    
    # Clear session data
    if 'shipping_info' in request.session:
        del request.session['shipping_info']
    if 'pending_order_number' in request.session:
        del request.session['pending_order_number']
    if 'selected_item_ids' in request.session:
        del request.session['selected_item_ids']
    
    return render(request, 'cart/payment_success.html', {'order': order})
