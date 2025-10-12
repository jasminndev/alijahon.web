from django.contrib import admin
from django.contrib.admin import ModelAdmin
from parler.admin import TranslatableAdmin

from apps.models import Category, Product, AdminSetting, User, Payment


# Register your models here.


@admin.register(Category)
class CategoryAdmin(TranslatableAdmin):
    pass

@admin.register(Product)
class ProductAdmin(ModelAdmin):

    exclude = 'slug',

@admin.register(AdminSetting)
class AdminSettingAdmin(admin.ModelAdmin):
    pass

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    pass


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = 'card_number' , 'pay_amount' , 'pay_status' , 'receipt'

    def save_model(self, request, obj, form, change):
        data = form.cleaned_data
        if change and data.get('pay_status') == Payment.StatusPayType.CANCELED.value:
            owner = data.get("owner")
            owner.balance += data.get("pay_amount")
            owner.save()
        return super().save_model(request, obj, form, change)






