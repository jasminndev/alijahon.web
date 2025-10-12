from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import TemplateView, ListView, FormView, DetailView, UpdateView

from apps.forms import OrderModelForm, OrderUpdateModelForm
from apps.models import Order, Category, Region


class OperatorOrderListView(ListView):
    queryset = Order.objects.all()
    template_name = 'apps/operator/operator-page.html'
    context_object_name = 'orders'

    def post(self, request):
        category_id = request.POST.get('category_id')
        district_id = request.POST.get('district_id')
        query = self.get_queryset()
        if category_id:
            query = query.filter(product__category__id=category_id)
        if district_id:
            query = query.filter(district_id=district_id)
        context = {
            "status": Order.StatusType.values,
            "categories":Category.objects.all(),
            "orders": query
        }
        return render(request , 'apps/operator/operator-page.html' , context)

    def get_queryset(self):
        status = self.request.GET.get('status')
        query = super().get_queryset()
        return query.filter(status=status)


    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['status'] = Order.StatusType.values
        data['regions'] = Region.objects.all()
        data['categories'] = Category.objects.all()
        return data

class OrderDetailView(DetailView):
    queryset = Order.objects.all()
    template_name = 'apps/operator/order-change.html'
    pk_url_kwarg = 'pk'
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['regions'] = Region.objects.all()
        return data


class OrderUpdateView(UpdateView):
    queryset = Order.objects.all()
    template_name = 'apps/operator/order-change.html'
    pk_url_kwarg = 'pk'
    form_class = OrderUpdateModelForm
    success_url = reverse_lazy('operator')

    def form_valid(self, form):
        status = form.cleaned_data.get('status')
        obj = self.get_object(self.queryset)
        if obj.thread and status == Order.StatusType.COMPLETED.value:
            seller = obj.thread.owner
            seller.balance += (obj.product.seller_price - obj.thread.discount_price)*obj.quantity
            seller.save()
        return super().form_valid(form)









