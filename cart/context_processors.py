from .models import Cart

def cart_processor(request):
    """
    Context processor to make cart data available in all templates.
    """
    cart = None
    cart_total_items = 0
    
    if request.user.is_authenticated:
        try:
            cart = Cart.objects.get(user=request.user)
            cart_total_items = cart.items.count()
        except Cart.DoesNotExist:
            pass
    
    return {
        'cart': cart,
        'cart_total_items': cart_total_items
    }