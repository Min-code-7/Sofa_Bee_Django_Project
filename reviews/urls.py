from django.urls import path
from .views import filter_reviews

urlpatterns = [
    path("filter/<int:product_id>/", filter_reviews, name="filter_reviews"),
]
