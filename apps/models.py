from ckeditor_uploader.fields import RichTextUploadingField
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import AbstractUser, UserManager
from django.db.models import Model, SlugField, CharField, URLField, ImageField, DecimalField, PositiveIntegerField, \
    TextField, ForeignKey, CASCADE, SET_NULL
from django.db.models.enums import TextChoices
from django.db.models.fields import DateTimeField, DateField
from django.utils.text import slugify
from parler.models import TranslatableModel, TranslatedFields


# Create your models here.

class CustomUserManager(UserManager):
    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(phone_number, password, **extra_fields)

    create_superuser.alters_data = True

    async def acreate_superuser(
            self, phone_number, password=None, **extra_fields
    ):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return await self._acreate_user(phone_number, password, **extra_fields)

    def _create_user_object(self, phone_number, password, **extra_fields):
        if not phone_number:
            raise ValueError("The given phone_number must be set")

        user = self.model(phone_number=phone_number, **extra_fields)
        user.password = make_password(password)
        return user

    def _create_user(self, phone_number, password, **extra_fields):
        user = self._create_user_object(phone_number, password, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(phone_number, password, **extra_fields)

class BaseSlug(Model):
    slug = SlugField(unique=True)
    name = CharField(max_length=255)

    class Meta:
        abstract = True

    def save(self, **kwargs):
        slug = slugify(self.name)
        i = 1
        while self.__class__.objects.filter(slug=slug).exists():
            slug += f"-{i}"
            i += 1
        self.slug = slug
        super().save()

class Region(Model):
    name = CharField(max_length=255)

class District(Model):
    name = CharField(max_length=255)
    region = ForeignKey("apps.Region", CASCADE, related_name="districts")

class User(AbstractUser):
    class RoleType(TextChoices):
        SELLER = 'seller' , "Seller"
        OPERATOR = 'operator' , "Operator"
        ADMIN = 'admin' , "Admin"
        DELIVER = 'deliver' , "Deliver"
    phone_number = CharField(max_length=15, unique=True)
    objects = CustomUserManager()
    username = None
    email = None
    EMAIL_FIELD = None
    REQUIRED_FIELDS = []
    USERNAME_FIELD = "phone_number"
    district = ForeignKey("apps.District", SET_NULL, related_name="users", blank=True, null=True)
    address = CharField(max_length=255, blank=True, null=True)
    telegram_id = CharField(max_length=30, blank=True, null=True)
    about = TextField(blank=True, null=True)
    balance = DecimalField(max_digits=10 , decimal_places=0 , default=0)
    role = CharField(max_length=50 , choices=RoleType , default=RoleType.SELLER)

    @property
    def wishlist_products(self):
        return self.wishlists.values_list('product_id',flat=True)

class Category(TranslatableModel):
    icon = URLField()
    translations = TranslatedFields(
        title=CharField(max_length=200)
    )
    def __str__(self):
        return self.title

class Product(BaseSlug):
    image = ImageField(upload_to='products/')
    description = RichTextUploadingField()
    price = DecimalField(max_digits=10, decimal_places=0)
    discount = PositiveIntegerField()
    seller_price = DecimalField(max_digits=10, decimal_places=0)
    bonus_price = DecimalField(max_digits=10, decimal_places=0, null=True, blank=True)
    quantity = PositiveIntegerField()
    discount_text = TextField()
    telegram_post = URLField(null=True, blank=True)
    category = ForeignKey('apps.Category', CASCADE, related_name='products')

    @property
    def discount_price(self):
        price = int(self.price)
        return price - price * (self.discount / 100)

class WishList(Model):
    user = ForeignKey('apps.User' , CASCADE , related_name="wishlists")
    product = ForeignKey('apps.Product' , CASCADE , related_name="wishlists")
    created_at = DateTimeField(auto_now_add=True)

class Order(Model):
    class StatusType(TextChoices):
        NEW = "new" , "New"
        READY_TO_DELIVERY = "ready to delivery" , "Ready to delivery"
        DELIVERING = "delivering"  , "Delivering"
        DELIVERED = "delivered"  , "Delivered"
        COMPLETED = "completed"  , "Completed"
        NOT_PICK_UP_CALL = "not pick up call"  , "Not Pick Up Call"
        ARCHIVE = "archive"  , "Archive"
        CANCELED = "canceled" , "Canceled"


    owner = ForeignKey('apps.User' , SET_NULL ,related_name='owner_orders', null=True , blank=True)
    operator = ForeignKey('apps.User' , SET_NULL ,related_name='operator_orders', null=True , blank=True)
    product = ForeignKey('apps.Product' , SET_NULL , related_name='orders', null=True , blank=True)
    phone_number = CharField(max_length=20)
    first_name = CharField(max_length=255)
    district = ForeignKey('apps.District' , SET_NULL , null=True , blank=True)
    status = CharField(max_length=255 , choices=StatusType , default=StatusType.NEW)
    quantity = PositiveIntegerField(default=1)
    total = DecimalField(max_digits=9 , decimal_places=0)
    comment = TextField(null=True)
    thread = ForeignKey('apps.Thread' , SET_NULL , related_name='orders' , null=True , blank=True)
    deliver_time = DateField(null=True , blank=True)
    created_at = DateTimeField(auto_now_add=True)
    updated_at = DateTimeField(auto_now=True)


    @property
    def discount_price(self):
        price = float(self.product.discount_price) - (float(self.thread.discount_price) if self.thread else 0)
        return price

class Thread(Model):
    class Meta:
        default_related_name = "threads"
    owner = ForeignKey('apps.User' , CASCADE)
    product = ForeignKey('apps.Product' , CASCADE)
    name = CharField(max_length=255)
    discount_price = DecimalField(max_digits=9 , decimal_places=0)
    created_at = DateTimeField(auto_now_add=True)
    visit_count = PositiveIntegerField(default=0)

class AdminSetting(Model):
    deliver_price = DecimalField(max_digits=9 , decimal_places=0 , default=0)
    competition_thumbnail_img = ImageField(upload_to='competition/',null=True , blank=True)
    competition_description = RichTextUploadingField(null=True , blank=True)
    start_competition = DateField(null=True , blank=True)
    end_competition = DateField(null=True , blank=True)

class Payment(Model):
    class StatusPayType(TextChoices):
        CANCELED = 'canceled' , 'Canceled'
        UNDER_VIEW = 'under view' , 'Under View'
        COMPLETED = 'completed' , 'Completed'

    card_number = CharField(max_length=16)
    pay_amount = DecimalField(max_digits=9 , decimal_places=0)
    pay_status = CharField(choices=StatusPayType,  default=StatusPayType.UNDER_VIEW)
    owner = ForeignKey('apps.User' , SET_NULL , related_name='payments',null=True , blank=True)
    message = TextField(null=True , blank=True)
    receipt = ImageField(upload_to='payment/' , null=True , blank=True)
    created_at = DateTimeField(auto_now_add=True)
    update_at = DateTimeField(auto_now=True)

    def __str__(self):
        return self.card_number







