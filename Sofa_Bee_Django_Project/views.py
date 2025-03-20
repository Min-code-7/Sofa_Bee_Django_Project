from django.shortcuts import redirect

def home(request):
    # Redirect to products page
    return redirect('products:product_list')
