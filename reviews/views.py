from django.shortcuts import render
from django.http import JsonResponse
from .models import Review
from products.views import REVIEWS


# Create your views here.

def filter_reviews(request, product_id):

    rating = request.GET.get("rating")
    keyword = request.GET.get("keyword")
    only_images = request.GET.get("images") == "true"



    # reviews = Review.objects.filter(product_id=int(product_id))
    reviews = REVIEWS.get(product_id, [])
    print(f"All Reviews for Product {product_id}: {list(reviews)}")

    print(f"Received rating: {rating} (type: {type(rating)})")
    print(f"All Reviews for Product {product_id}: {reviews}")

    if rating:
        reviews = [r for r in reviews if r["rating"] == int(rating)]



    if only_images:
        reviews = reviews.exclude(image="")

    if keyword:
        reviews = reviews.filter(comment__icontains=keyword)

    for review in reviews:
        print(f"Review rating type: {type(review['rating'])}, value: {review['rating']}")

    review_data = [
        {
            "user": review["user"],
            "rating": review["rating"],
            "comment": review["comment"],
            "created_at": review["created_at"],
            "image": review.get("image", None)
        }
        for review in reviews
    ]

    return JsonResponse({"reviews": review_data})