from django.core.management.base import BaseCommand
from products.models import Product, Category
import random


class Command(BaseCommand):
    help = 'Generate 200 sample products'

    def handle(self, *args, **kwargs):

        products = []
        categories = list(Category.objects.all())
        self.stdout.write(str(categories))

        for i in range(1, 201):
            product = Product(
                name =f'Test Phone {i}',
                description=f'This is the description for Test Phone {i}.',
                price=100 + i,
                stock= random.randint(1, 20),
                category = random.choice(categories))

            products.append(product)

        Product.objects.bulk_create(products)

        self.stdout.write(
            self.style.SUCCESS(
                'Successfully created 200 products.'
            )
        )