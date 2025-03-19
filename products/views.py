from itertools import product

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.templatetags.static import static
from django.contrib import messages
from django.core.paginator import Paginator

from reviews.forms import ReviewForm
from .forms import ProductForm
from .models import Product, Category

# just test
PRODUCTS = [
    {"id": 1, "name": "test product 1", "description": "This is the first test product", "category": "Makeup", "price": 99.99, "image": static("products/images/pic1.png")},
    {"id": 2, "name": "test product 2", "description": "This is the second test product", "category": "Clothing", "price": 199.99, "image": static("products/images/pic2.png")},
    {"id": 3, "name": "test product 3", "description": "This is the third test product", "category": "Electronics", "price": 299.99, "image": static("products/images/pic3.png")},
    {"id": 4, "name": "test product 4", "description": "This is the first test product","category": "Makeup", "price": 99.99,
     "image": static("products/images/pic4.png")},
    {"id": 5, "name": "test product 5", "description": "This is the fifth test product", "category": "Electronics", "price": 199.99,
     "image": static("products/images/pic5.png")},
    {"id": 6, "name": "test product 6", "description": "This is the sixth test product", "category": "Clothing", "price": 299.99,
     "image": static("products/images/pic6.png")},
    {"id": 7, "name": "test product 7", "description": "This is the seventh test product","category": "Makeup", "price": 99.99,
     "image": static("products/images/pic7.png")},
    {"id": 8, "name": "test product 8", "description": "This is the eighth test product", "category": "Electronics", "price": 199.99,
     "image": static("products/images/pic8.png")},
    {"id": 9, "name": "test product 9", "description": "This is the ninth test product", "category": "Electronics", "price": 299.99,
     "image": static("products/images/pic9.png")},
    {"id": 10, "name": "test product 10", "description": "This is the tenth test product", "category": "Clothing", "price": 99.99,
     "image": static("products/images/pic10.png")},
    {"id": 11, "name": "test product 11", "description": "This is the eleventh test product", "category": "Makeup", "price": 199.99,
     "image": static("products/images/pic11.png")},
    {"id": 12, "name": "test product 12", "description": "This is the twelfth test product", "category": "Clothing", "price": 299.99,
     "image": static("products/images/pic12.png")},
]

REVIEWS = {
    1: [
        {"user": "UserA", "rating": 5, "comment": "Very good!", "created_at": "2025-03-06 12:05:30"},
        {"user": "UserC", "rating": 2, "comment": "Bad!", "created_at": "2025-03-06 12:05:30"}
    ],
    3: [
        {"user": "UserD", "rating": 4, "comment": "Good!", "created_at": "2025-03-06 12:05:30"},
        {"user": "UserB", "rating": 3, "comment": "Very good!", "created_at": "2025-03-06 12:05:30"},
        {"user": "UserA", "rating": 3, "comment": "Very good!", "created_at": "2025-03-06 12:05:30"}
    ],
    6: [
        {"user": "UserD", "rating": 5, "comment": "Very good!", "created_at": "2025-03-06 12:05:30"}
    ]
}


# Create your views here.
'''
def product_list(request):
    products = Product.objects.all()
    return render(request, 'products/product_list.html', {'products': products})
'''
# testing product_list function
def product_list(request):

    # get keyword
    query = request.GET.get('q', '').strip().lower()
    # print("keywords: ", query)

    # get category
    category_name = request.GET.get('category', '')

    products = Product.objects.all()

    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    if category_name:
        products = products.filter(category__name__icontains=category_name)

    categories = Category.objects.all()

    # paginator
    paginator = Paginator(products, 9)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    return render(request, "products/product_list.html", {"products": products, "query": query, "categories": categories, "selected_category": category_name})


def product_detail(request, product_id):


    # use sqlite
    product = get_object_or_404(Product, id=product_id)
    # return render(request, 'products/product_detail.html', {'product': product})
    # use test data
    # product = next((p for p in PRODUCTS if p["id"] == product_id), None)


    if product is None:
        return render(request, "404.html", {"message": "No Product matches the given query."}, status=404)

    # get review
    reviews = product.reviews.all()


    # handle review filter
    for review in reviews:
        review["rating"] = int(review["rating"])
        review["stars"] = range(review["rating"])

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, "products/product_detail.html", {"product": product, "reviews": reviews, "form": form})

def product_search(request):
    query = request.GET.get('q', '')
    # products = Product.objects.filter(name__icontains=query)
    category = request.GET.get('category', '').strip().lower()

    products = Product.objects.all()

    """
    data = {
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'image': product.image.url if product.name else None,
                'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
             }
            for product in products
        ]
    }
    """
    if query:
        products = products.filter(name__icontains=query) | products.filter(description__icontains=query)

    if category:
        products = products.filter(category__name__iexact=category)

    data = {
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'image': product.image.url if product.image else None,
                'created_at': product.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(product,
                                                                                          'created_at') else '',
            }
            for product in products
        ]
    }

    return JsonResponse(data)


@login_required
def add_product(request):
    if not hasattr(request.user, "userprofile") or request.user.userprofile.user_type != 'merchant':
        messages.error(request, "You are not allowed to add product.")
        return redirect('products:product_list')

    Category.create_default_categories()

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = request.user
            product.save()
            return redirect('products:product_list')
    else:
        form = ProductForm()

    return render(request, 'products/add_product.html', {'form': form})


def filter_category(request):
    category = request.GET.get('category', None)

    if category:
        products = Product.objects.filter(category__name__icontains=category)
    else:
        products = Product.objects.all()

    data = {
        'products': [
            {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'image': product.image.url if product.image else None,
            }
            for product in products
        ]
    }

    return JsonResponse(data)
