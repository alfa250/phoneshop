from django.test import TestCase
from products.models import Product, Category, Order, OrderItem
from django.contrib.auth.models import User
from decimal import Decimal



class ProductModelTest(TestCase):

    def test_product_can_be_created(self):
        product = Product.objects.create(
            name='iphone 14',
            description='A smartphone by Apple',
            price=9.99,
            stock=10,
        )

        self.assertEqual(product.name, 'iphone 14')
        self.assertEqual(product.price, 9.99)
        self.assertEqual(product.stock, 10)

    def test_current_price_returns_regular_price_when_not_on_sale(self):
        product = Product.objects.create(
            name='iphone 14',
            description='A smartphone by Apple',
            price=9.99,
            stock=10,
            is_sale = False
        )

        self.assertEqual(product.current_price, product.price)

    def test_current_price_returns_sale_price_when_on_sale(self):
        product = Product.objects.create(
            name='iphone 14',
            description='A smartphone by Apple',
            price=9.99,
            stock=10,
            is_sale = True,
            sale_price = 5.99
        )

        self.assertEqual(product.current_price, product.sale_price)


class OrderItemModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.product = Product.objects.create(
            name='iphone 14',
            description='A smartphone by Apple',
            price=9.99,
            stock=10,
        )
        self.order = Order.objects.create(
            user=self.user,
            total=1)

    def test_order_item_can_be_created(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=19.98
        )

        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, 19.98)

    def test_subtotal_is_calculated_correctly(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=9.99
        )

        self.assertEqual(order_item.subtotal, 19.98)
        

    def test_order_item_keeps_purchase_price_even_if_product_price_changes(self):
        order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=9.99
        )

        # Change the product price
        self.product.price = Decimal('19.99')
        self.product.save()
        order_item.refresh_from_db()

        

        # The order item price should remain the same
        self.assertEqual(order_item.price, Decimal('9.99'))


class OrderModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        
    def test_first_order_number_is_1001(self):
        order = Order.objects.create(
            user=self.user)
        
        self.assertEqual(order.order_number, 1001)

    def test_new_order_is_pending_by_default(self):
        order = Order.objects.create(
            user=self.user)
        
        self.assertEqual(order.status, 'Pending')

    def test_order_number_does_not_change_on_update(self):
        order = Order.objects.create(
            user=self.user)
        
        original_order_number = order.order_number
        order.status = 'confirmed'
        order.save()
        
        self.assertEqual(order.order_number, original_order_number)

    def test_order_items_relationship(self):
        order = Order.objects.create(
            user=self.user)
        
        product1 = Product.objects.create(
            name='iphone 14',
            description='A smartphone by Apple',
            price=9.99,
            stock=10,
        )
        
        product2 = Product.objects.create(
            name='Samsung Galaxy S21',
            description='A smartphone by Samsung',
            price=8.99,
            stock=15,
        )
        
        order_item1 = OrderItem.objects.create(
            order=order,
            product=product1,
            quantity=1,
            price=9.99
        )
        
        order_item2 = OrderItem.objects.create(
            order=order,
            product=product2,
            quantity=2,
            price=17.98
        )
        
        self.assertEqual(order.items.count(), 2)
        self.assertIn(order_item1, order.items.all())
        self.assertIn(order_item2, order.items.all())

    def test_order_total_calculation(self):
        order = Order.objects.create(
            user=self.user)
        
        product1 = Product.objects.create(
            name='iphone 14',
            description='A smartphone by Apple',
            price=9.99,
            stock=10,
        )
        
        product2 = Product.objects.create(
            name='Samsung Galaxy S21',
            description='A smartphone by Samsung',
            price=8.99,
            stock=15,
        )
        
        OrderItem.objects.create(
            order=order,
            product=product1,
            quantity=1,
            price=9.99
        )
        
        OrderItem.objects.create(
            order=order,
            product=product2,
            quantity=2,
            price=17.98
        )
        
        # Calculate total
        total = sum(item.subtotal for item in order.items.all())
        order.total = total
        order.save()
        
        self.assertEqual(order.total, Decimal('45.95'))  # 9.99 + 17.98

    def test_customer_information_is_stored_correctly(self):
        order = Order.objects.create(
            user=self.user,
            full_name='John Doe',
            phone='1234567890',
            address='123 Main St',
            city='Anytown',
            state='Anystate'
        )
        
        self.assertEqual(order.full_name, 'John Doe')
        self.assertEqual(order.phone, '1234567890')
        self.assertEqual(order.address, '123 Main St')
        self.assertEqual(order.city, 'Anytown')
        self.assertEqual(order.state, 'Anystate')
    
    def test_order_total_is_stored_correctly(self):
        order = Order.objects.create(
            user=self.user,
            total= Decimal('45.95')
        )
        
        self.assertEqual(order.total, Decimal('45.95'))