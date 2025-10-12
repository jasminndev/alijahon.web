from django.urls import path

from apps.views import PaymentCreateView

urlpatterns = [
    path("payment-form", PaymentCreateView.as_view(), name='payment-form'),

]