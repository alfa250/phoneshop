from django.db import models
from email.policy import default
import uuid
from django.contrib.auth.models import User, AbstractUser


# Create your models here.

class Product(models.Model):
    name =  models.CharField(max_length = 100)
    description = models.TextField()
    price = models.DecimalField(max_digits = 10, decimal_places = 2)
    image = models.ImageField(upload_to = 'products/', null = True, blank = True)
    stock = models.PositiveIntegerField()
    is_sale = models.BooleanField(default = False)
    sale_price = models.DecimalField(max_digits = 10, decimal_places = 2, null = True, blank = True)

    @property
    def current_price(self):
        if self.is_sale and self.sale_price:
            return self.sale_price
        return self.price


class Order(models.Model):

    class StatusChoices(models.TextChoices):
        PENDING =  'Pending'
        CONFIRMED =  'Confirmed'
        CANCELED = 'Canceled'
    order_id = models.UUIDField(primary_key = True, default = uuid.uuid4)
    user = models.ForeignKey(User, on_delete = models.CASCADE)
    date_created = models.DateTimeField(auto_now_add = True)
    status = models.CharField(
        choices = StatusChoices.choices,
        default = StatusChoices.PENDING
    )
    product = models.ManyToManyField(Product, through = 'OrderItem', related_name = 'orders')


    def __str__(self):
        return f'Order {self.order_id} by {self.user.username} is {self.status}'

#this is going to create a join table linking the product table to the order table.
class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete = models.CASCADE,
        related_name = 'items')
    product = models.ForeignKey(Product, on_delete = models.CASCADE)
    quantity = models.PositiveIntegerField()


    
