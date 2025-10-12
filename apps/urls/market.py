from django.urls import path

from apps.views import MarketListView, ThreadCreateView, ThreadListView, ThreadProductDetail, StatisticListView, \
    CompetitionListView, DiagramTemplateView, diagram_statistic_view

urlpatterns = [
    path("market", MarketListView.as_view(), name='market'),
    path("market/thread", ThreadCreateView.as_view(), name='thread-form'),
    path("market/thread-list", ThreadListView.as_view(), name='thread-list'),
    path("oqim/<int:pk>", ThreadProductDetail.as_view(), name='thread-list'),
    path("oqim/statistic", StatisticListView.as_view(), name='thread-statistic'),
    path("oqim/competition", CompetitionListView.as_view(), name='competition'),
    path("market/diagram", DiagramTemplateView.as_view(), name='diagram'),
    path("order/diagram", diagram_statistic_view, name='diagram_statistic'),
]