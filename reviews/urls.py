from django.urls import path
from .views import filter_reviews, add_review

app_name = 'reviews'

urlpatterns = [
    path("filter/<int:product_id>/", filter_reviews, name="filter_reviews"),
    path("add/<int:product_id>/", add_review, name="add_review"),
]
