from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from products.models import Order, OrderItem, Product
from django.core.cache import cache


User = get_user_model()


class OrderAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        self.product = Product.objects.create(
            name='Test Phone',
            description='A test phone',
            price=100.00,
            stock=10
        )

        self.order = Order.objects.create(
            user=self.user,
            full_name='Test User',
            phone='08000000000',
            address='Test Address',
            city='Abuja',
            state='FCT',
            total=200.00
        )

        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=100.00
        )

    def test_authenticated_user_can_list_orders(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.get('/api/orders/')

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['user'], self.user.id)

    def test_user_cannot_access_another_users_orders(self):
        another_user = User.objects.create_user(
            username='anotheruser',
            password='anotherpassword123'
        )
        other_order = Order.objects.create(
        user=another_user,
        full_name='anotheruser',
        phone='08111111111',
        address='Other Address',
        city='Abuja',
        state='FCT',
        total=100.00
    )

        self.client.force_authenticate(user=self.user)

        response = self.client.get(
            f'/api/orders/{other_order.order_id}/'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
    def test_unauthenticated_user_cannot_list_orders(self):
        response = self.client.get('/api/orders/')

        self.assertEqual(
            response.status_code,
            status.HTTP_401_UNAUTHORIZED
        )

class ProductAPITestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword123',
            is_staff = True
        )

    def test_authenticated_user_cannot_create_product_with_invalid_data(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'Invalid Product',
            'description': 'This product has invalid data',
            'price': -100,
            'stock': -5,
        }

        response = self.client.post(
            '/api/products/',
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_admin_cannot_create_product_with_negative_stock(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'name': 'Invalid Stock Product',
            'description': 'A product with invalid stock',
            'price': 100.00,
            'stock': -5,
        }

        response = self.client.post(
            '/api/products/',
            data
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )

    def test_product_creation_invalidates_cache(self):
        #create the initial cached response
        response = self.client.get('/api/products/')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        
        #create a new product
        self.client.force_authenticate(user=self.user)
        data = {
            'name': 'New Product',
            'description': 'A new product',
            'price': 150.00,
            'stock': 20,
        }
        response = self.client.post(
            '/api/products/',
            data,
            format='json'
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        response = self.client.get('/api/products/')
        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        product_names = [product['name'] for product in response.data]
        self.assertIn('New Product', product_names)
        




