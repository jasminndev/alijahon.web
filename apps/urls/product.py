from os import getpid

from django.urls import path
from apps.views import HomeListView, ProductListView, ProductDetailView, SearchListView

urlpatterns = [
    path("", HomeListView.as_view(), name='home'),
    path("products-list", ProductListView.as_view(), name="product-list"),
    path("product/detail/<str:slug>", ProductDetailView.as_view(), name="product-detail"),
    path("product/search", SearchListView.as_view(), name="search")
]


getpid()