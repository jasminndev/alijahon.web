from django.urls import path

from apps.views import HomeListView, ProductListView, AuthFormView, ProfileUpdateView, LogoutView, \
    district_list, ChangePasswordFormView, wishlist, WishlistView, ProductDetailView, OrderCreateView, OrderListView, \
    MarketListView, ThreadCreateView, ThreadListView , ThreadProductDetail , SearchListView , StatisticListView , CompetitionListView

urlpatterns = [
    path("user/auth", AuthFormView.as_view(), name='auth'),
    path("user/profile/<int:pk>", ProfileUpdateView.as_view(), name='profile'),
    path("user/logout", LogoutView.as_view(), name='logout'),
    path("user/district/list", district_list, name='district_list'),
    path("user/change/password", ChangePasswordFormView.as_view(), name='change-password'),
    path("user/wishlist/<int:product_id>", wishlist, name='wishlist'),
    path("user/like/list", WishlistView.as_view(), name='wish-list'),
]