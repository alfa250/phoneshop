from django.test import TestCase
from rest_framework.test import  APIClient
from decimal import Decimal
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from products.models import Product, Category



class ProductAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )

        self.category = Category.objects.create(
            name='Smartphones',
            description='Mobile smartphones'
        )

    def test_product_list_endpoint_returns_200(self):
        response = self.client.get('/api/products/')

        self.assertEqual(response.status_code, 200)

    def test_authenticated_user_can_create_product_in_database(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'iPhone 16',
            'description': 'An Apple smartphone',
            'price': '1200000.00',
            'stock': 10,
            'category': self.category.pk,
        }

        response = self.client.post(
            '/api/products/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, 201)

        product = Product.objects.get(
            name='iPhone 16'
        )

        self.assertEqual(
            product.description,
            'An Apple smartphone'
        )

        self.assertEqual(
            product.price,
            Decimal('1200000.00')
        )

        self.assertEqual(
            product.stock,
            10
        )

        self.assertEqual(
            product.category,
            self.category
        )

    

    