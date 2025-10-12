from django.urls import path

from apps.views import OrderCreateView, OrderListView , RequestTemplateView

urlpatterns = [
    path("order/form", OrderCreateView.as_view(), name='order'),
    path("order/list", OrderListView.as_view(), name='order-list'),
    path("request/list", RequestTemplateView.as_view(), name='request-list'),
]