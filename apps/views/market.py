from datetime import datetime, timedelta

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Count, F, Sum
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, FormView, TemplateView, UpdateView, DetailView, CreateView

from apps.forms import AuthForm, ProfileModelForm, PasswordForm, OrderModelForm, ThreadModelForm
from apps.models import Category, Product, User, Region, District, WishList, Order, AdminSetting, Thread


class MarketListView(ListView):
    queryset = Product.objects.all()
    template_name = "apps/market/market-list.html"
    context_object_name = "products"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        slug = self.request.GET.get("category")
        data['slug'] = slug
        if not slug in ("all", 'top'):
            data['products'] = data.get('products').filter(category__slug=slug)
        elif slug == 'top':
            data['products'] = data.get('products').annotate(
                order_count=Count('orders', filter=Q(orders__status=Order.StatusType.COMPLETED))).order_by(
                '-order_count')[:10]
        data['categories'] = Category.objects.all()
        return data


class ThreadCreateView(CreateView):
    queryset = Thread.objects.all()
    form_class = ThreadModelForm
    template_name = 'apps/market/market-list.html'
    success_url = reverse_lazy('thread-list')

    def form_valid(self, form):
        object = form.save(commit=False)
        object.owner = self.request.user
        object.save()
        self.object = object
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)


class ThreadListView(ListView):
    queryset = Thread.objects.all()
    template_name = 'apps/market/thread-list.html'
    context_object_name = 'threads'

    def get_queryset(self):
        return super().get_queryset().filter(owner=self.request.user)


class ThreadProductDetail(DetailView):
    queryset = Thread.objects.all()
    template_name = "apps/product-detail.html"
    context_object_name = 'thread'
    pk_url_kwarg = 'pk'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        thread = self.get_object(self.get_queryset())
        thread.visit_count += 1
        thread.save()
        product = self.get_object(self.get_queryset()).product
        data['product'] = product
        data['discount_price'] = float(product.discount_price) - float(data.get("thread").discount_price)
        return data


class StatisticListView(ListView):
    queryset = Thread.objects.all()
    template_name = 'apps/market/statistics.html'
    context_object_name = 'threads'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        dict_data = self.get_queryset().aggregate(
            visit_total=Sum('visit_count'),
            new_total=Sum('new_count'),
            ready_to_delivery_total=Sum('ready_to_delivery_count'),
            delivering_total=Sum('delivering_count'),
            delivered_total=Sum('delivered_count'),
            not_pick_total=Sum('not_pick_count'),
            canceled_total=Sum('canceled_count'),
            archive_total=Sum('archive_count'),
        )
        data.update(dict_data)
        return data

    def get_queryset(self):
        query = super().get_queryset()
        period = self.request.GET.get('period')

        now = datetime.now()
        today_start = datetime(now.year, now.month, now.day, 0, 0, 0)
        today_end = datetime(now.year, now.month, now.day, 23, 59, 59)

        # Yesterday
        yesterday_start = today_start - timedelta(days=1)
        yesterday_end = today_end - timedelta(days=1)

        # Weekly
        week_start = today_start - timedelta(days=6)  # Including today, so 7 days total
        week_end = today_end

        # Monthly (30 kunlik)
        month_start = today_start - timedelta(days=29)
        month_end = today_end

        # All time
        all_start = datetime(2000, 1, 1, 0, 0, 0)
        all_end = today_end

        datetime_map = {
            "today": [today_start, today_end],
            "last_day": [yesterday_start, yesterday_end],
            "weekly": [week_start, week_end],
            "monthly": [month_start, month_end],
            "all": [all_start, all_end],
        }
        filter_time = datetime_map.get(period)
        query = query.filter(owner=self.request.user).filter(created_at__range=filter_time).annotate(
            new_count=Count('orders', filter=Q(orders__status=Order.StatusType.NEW)),
            ready_to_delivery_count=Count('orders', filter=Q(orders__status=Order.StatusType.READY_TO_DELIVERY)),
            delivering_count=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERING)),
            delivered_count=Count('orders', filter=Q(orders__status=Order.StatusType.DELIVERED)),
            not_pick_count=Count('orders', filter=Q(orders__status=Order.StatusType.NOT_PICK_UP_CALL)),
            canceled_count=Count('orders', filter=Q(orders__status=Order.StatusType.CANCELED)),
            archive_count=Count('orders', filter=Q(orders__status=Order.StatusType.ARCHIVE)),
        ).values('name',
                 'product__name',
                 "visit_count",
                 'new_count',
                 'ready_to_delivery_count',
                 'delivering_count',
                 'delivered_count',
                 'not_pick_count',
                 'canceled_count',
                 'archive_count')
        return query


class CompetitionListView(ListView):
    queryset = User.objects.all()
    template_name = 'apps/market/competition.html'
    context_object_name = 'users'

    def get_context_data(self, **kwargs ):
        data = super().get_context_data()
        data['setting'] = AdminSetting.objects.first()
        return data
    def get_queryset(self):
        query = super().get_queryset()
        obj = AdminSetting.objects.first()
        start = obj.start_competition
        end = obj.end_competition
        query = query.filter(threads__orders__created_at__range=[start, end]).annotate(
            orders_count=Count('threads__orders', filter=Q(threads__orders__status=Order.StatusType.COMPLETED))
        ).filter(orders_count__gt=0).order_by('-orders_count').values('pk','first_name', 'orders_count')
        return query


class DiagramTemplateView(TemplateView):
    template_name = 'apps/market/diagram.html'


def diagram_statistic_view(request):
    data = {
        "regions" : [
        'Toshkent', 'Andijon', 'Buxoro', 'Fargona', 'Jizzax', 'Namangan',
        'Navoiy', 'Qashqadaryo', 'Qoraqalpog‘iston', 'Samarqand',
        'Sirdaryo', 'Surxondaryo', 'Toshkent viloyati', 'Xorazm'
    ],
        "numbers":[150, 90, 75, 120, 65, 110, 55, 80, 70, 130, 60, 85, 140, 50]
    }
    return JsonResponse(data)
