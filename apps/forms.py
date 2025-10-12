import re

from django.contrib.auth.hashers import make_password, check_password
from django.core.exceptions import ValidationError
from django.forms import Form, ModelForm
from django.forms.fields import CharField, IntegerField

from apps.models import User, Order, AdminSetting, Thread, Product, Payment


class AuthForm(Form):
    phone_number = CharField(max_length=20)
    password = CharField(max_length=15)


    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        return  re.sub(r'\D', '', str(phone_number))

    def clean_password(self):
        password = self.cleaned_data.get("password")
        return make_password(str(password))

    def is_exists(self):
        phone_number = self.cleaned_data.get("phone_number")
        password = self.data.get("password")
        query = User.objects.filter(phone_number=phone_number)
        if not query.exists():
            user = User.objects.create_user(phone_number)
            user.set_password(password)
            user.save()
        else:
            user = query.first()
            if check_password(password , user.password):
                return user



    def save(self):
        phone_number = self.cleaned_data.get("phone_number")
        password = self.cleaned_data.get("password")
        return User.objects.create_user(phone_number=phone_number , password=password)


class ProfileModelForm(ModelForm):
    class Meta:
        model = User
        fields = "first_name" , "last_name" , "district" , "address" , "telegram_id" , "about"
        extra_kwargs = {
            "district": {"required" : False}
        }


class PasswordForm(Form):
    old_password = CharField(max_length=10)
    new_password = CharField(max_length=10)
    confirm_password = CharField(max_length=10)

    def clean_confirm_password(self):
        new_password = self.cleaned_data.get("new_password")
        confirm_password = self.cleaned_data.get("confirm_password")
        if new_password != confirm_password:
            raise ValidationError("Confirm passwordda xatolik!")



class OrderModelForm(ModelForm):
    class Meta:
        model = Order
        fields = 'first_name' , "phone_number" , "owner" , "product" , "thread"

    def save(self, commit = True):
        obj = super().save(commit=False)
        admin_setting  = AdminSetting.objects.first()
        obj.total = float(admin_setting.deliver_price) + float(obj.product.discount_price) - (float(obj.thread.discount_price) if obj.thread else 0)
        obj.save()
        return obj

class OrderUpdateModelForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['quantity'].required = False
        self.fields['deliver_time'].required = False
    class Meta:
        model = Order
        fields = 'quantity' , 'deliver_time' , 'status' , 'comment' , 'district'




class ThreadModelForm(ModelForm):
    class Meta:
        model = Thread
        fields = 'name' , 'discount_price' , 'product'

    def clean_discount_price(self):
        product_id = self.data.get('product')
        discount_price = self.cleaned_data.get('discount_price')
        product = Product.objects.filter(id=product_id).first()
        if product.seller_price < discount_price:
            raise ValidationError('Chegirma miqdori oshib ketdi !')
        return discount_price


    def clean_product(self):
        product_id = self.data.get('product')
        return Product.objects.filter(id=product_id).first()



class PaymentModelForm(ModelForm):
    class Meta:
        model = Payment
        fields = 'card_number' , 'pay_amount' , 'owner'

    def clean_pay_amount(self):
        owner_id = self.data.get('owner')
        pay_amount = self.cleaned_data.get('pay_amount')
        owner = User.objects.get(pk=owner_id)
        if owner.balance < pay_amount:
            raise ValidationError(f"Balance da pul yetarli emas")
        return pay_amount



