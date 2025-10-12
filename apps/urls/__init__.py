from apps.urls.product import urlpatterns as product_url
from apps.urls.market import urlpatterns as market_url
from apps.urls.order import urlpatterns as order_url
from apps.urls.user import urlpatterns as user_url
from apps.urls.payment import urlpatterns as payment_url
from apps.urls.operator import urlpatterns as operator_url

urlpatterns = [
    *product_url,
    *market_url,
    *order_url,
    *user_url,
    *payment_url,
    *operator_url
]
