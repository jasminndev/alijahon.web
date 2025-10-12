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


class AuthFormView(FormView):
    form_class = AuthForm
    template_name = 'apps/auth/login.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        if form.is_valid():
            user = form.is_exists()
            if user == None:
                messages.error(self.request, 'Password xato !')
                return redirect('auth')
            login(self.request, user)

        return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    queryset = User.objects.all()
    form_class = ProfileModelForm
    template_name = 'apps/auth/profile.html'
    login_url = reverse_lazy('auth')
    pk_url_kwarg = "pk"
    success_url = reverse_lazy("profile")

    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['regions'] = Region.objects.all()
        return data

    def get_success_url(self):
        return reverse('profile', kwargs={"pk": self.request.user.pk})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('home')


def district_list(request):
    region_id = request.GET.get("region_id")
    districts = District.objects.filter(region_id=region_id)
    data = [{"id": i.pk, "name": i.name} for i in districts]
    return JsonResponse(data, safe=False)


class ChangePasswordFormView(FormView):
    form_class = PasswordForm
    template_name = 'apps/auth/profile.html'
    success_url = reverse_lazy('profile')

    def form_valid(self, form):
        if form.is_valid():
            old_password = form.cleaned_data.get("old_password")
            new_password = form.cleaned_data.get("new_password")
            hash_password = self.request.user.password
            if check_password(old_password, hash_password):
                user = self.request.user
                user.set_password(new_password)
                user.save()
                login(self.request, user)
                messages.success(self.request, "Parol muvaffiqiyatli!")
                return super().form_valid(form)

    def form_invalid(self, form):
        for error in form.errors.values():
            messages.error(self.request, error)
        return super().form_invalid(form)

    def get_success_url(self):
        return reverse('profile', kwargs={"pk": self.request.user.pk})


def wishlist(request, product_id):
    query = WishList.objects.filter(user=request.user, product_id=product_id)
    if query.exists():
        query.delete()
        return JsonResponse({"liked": False})
    else:
        WishList.objects.create(user=request.user, product_id=product_id)
        return JsonResponse({"liked": True})


class WishlistView(LoginRequiredMixin, ListView):
    login_url = reverse_lazy('auth')
    queryset = WishList.objects.order_by('-created_at')
    template_name = 'apps/wishlist.html'
    context_object_name = "wishlists"

    def get_queryset(self):
        query = super().get_queryset()
        query = query.filter(user=self.request.user)
        return query
