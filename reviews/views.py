from django.shortcuts import render
from django.http import JsonResponse
from .models import Review
from products.views import REVIEWS


# Create your views here.

def filter_reviews(request, product_id):
    rating = request.GET.get("rating")
    keyword = request.GET.get("keyword", "").strip().lower()
    only_images = request.GET.get("images") == "true"

    product_id = int(product_id)



    reviews = REVIEWS.get(product_id, [])



    if rating:
        reviews = [r for r in reviews if r["rating"] == int(rating)]

    if only_images:
        reviews = [r for r in reviews if "image" in r and r["image"]]

    if keyword:
        reviews = [r for r in reviews if keyword in r["comment"].lower()]

    print(f"Filtered Reviews: {reviews}")

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
