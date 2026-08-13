from django.db import models
from email.policy import default
import uuid
from django.contrib.auth.models import User, AbstractUser


# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length = 100, unique = True)
    description = models.TextField()
    
    class Meta:
        verbose_name_plural = 'Categories'
        

    def __str__(self):
        return self.name


class Product(models.Model):
    name =  models.CharField(max_length = 100)
    description = models.TextField()
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    image = models.ImageField(upload_to = 'products/', null = True, blank = True)
    stock = models.PositiveIntegerField()
    is_sale = models.BooleanField(default = False)
    sale_price = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)
    category = models.ForeignKey(
    Category,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name="products"
)
    @property
    def current_price(self):
        if self.is_sale and self.sale_price:
            return self.sale_price
        return self.price


class Order(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING = 'Pending'
        CONFIRMED = 'Confirmed'
        CANCELED = 'Canceled'

    order_id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    order_number = models.PositiveIntegerField(
    unique=True,
    editable=False
)

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    full_name = models.CharField(max_length=100, blank = True)
    phone = models.CharField(max_length=20, blank = True)
    address = models.TextField(blank = True)
    city = models.CharField(max_length=100, blank = True)
    state = models.CharField(max_length=100, blank = True)

    date_created = models.DateTimeField(auto_now_add=True)

    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )

    product = models.ManyToManyField(
        Product,
        through='OrderItem',
        related_name='orders'
    )
    total = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0.00
    )
    def save(self, *args, **kwargs):
        if not self.order_number:
            last_order = Order.objects.order_by('-order_number').first()

            if last_order:
                self.order_number = last_order.order_number + 1
            else:
                self.order_number = 1001

        super().save(*args, **kwargs)

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete = models.CASCADE,
        related_name = 'items')
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
    max_digits=10,
    decimal_places=2,
    default=0.00
    )
    @property
    def subtotal(self):
        return self.quantity * self.price

        



    

    
