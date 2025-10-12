from django.urls import path
from apps.views import OperatorOrderListView,OrderDetailView,OrderUpdateView

urlpatterns = [
    path("operator/panel", OperatorOrderListView.as_view(), name='operator'),
    path("operator/panel/order/detail/<int:pk>", OrderDetailView.as_view(), name='order'),
    path("operator/panel/order/update/<int:pk>", OrderUpdateView.as_view(), name='order-update'),
]