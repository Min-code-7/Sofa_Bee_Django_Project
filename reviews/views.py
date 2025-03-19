from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import Review
from products.models import Product
from .forms import ReviewForm


# Create your views here.
def filter_reviews(request, product_id):
    rating = request.GET.get("rating")
    keyword = request.GET.get("keyword", "").strip().lower()
    only_images = request.GET.get("images") == "true"

    product = get_object_or_404(Product, id=product_id)


    reviews = Review.objects.filter(product=product)

    if rating:
        reviews = reviews.filter(rating=int(rating))

    if keyword:
        reviews = reviews.filter(comment__icontains=keyword)

    if only_images:
        reviews = reviews.exclude(image='')

    print(f"Filtered Reviews: {reviews}")

    review_data = [
        {
            "user": review.user.username,
            "rating": review.rating,
            "comment": review.comment,
            "created_at": review.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "image": review.image.url if review.image else None,
        }
        for review in reviews
    ]

    return JsonResponse({"reviews": review_data})


@login_required
def add_review(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    if request.method == 'POST':
        form = ReviewForm(request.POST, request.FILES)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            return redirect('products:product_detail', product_id=product.id)

    return redirect('products:product_detail', product_id=product.id)
