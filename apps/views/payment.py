from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView

from apps.forms import PaymentModelForm
from apps.models import Payment


class PaymentCreateView(CreateView):
    form_class = PaymentModelForm
    success_url = reverse_lazy('payment-form')
    template_name = 'apps/payment/payment-form.html'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['payments'] = Payment.objects.filter(owner=self.request.user).order_by('-created_at')
        return data
    def form_valid(self, form):
        owner = form.cleaned_data.get("owner")
        owner.balance -= form.cleaned_data.get('pay_amount')
        owner.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)


