from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from products.admin import OrderAdmin
from django.test import RequestFactory
from products.admin import ProductAdmin
from products.models import Product, Order, OrderItem, Category
from products.admin import ProductAdmin, StockStatusFilter


class OrderAdminTest(TestCase):

    def setUp(self):
        User = get_user_model()

        self.user = User.objects.create_user(
            username='customer',
            password='password123'
        )

        self.product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=300000,
            stock=10
        )
        self.product2 = Product.objects.create(
            name='Samsung S24',
            description='Samsung smartphone',
            price=250000,
            stock=15
)

        self.order = Order.objects.create(
            user=self.user,
            full_name='John Doe',
            phone='08012345678',
            address='123 Main Street',
            city='Abuja',
            state='FCT',
            total=600000,
            status=Order.StatusChoices.PENDING
        )

        self.order_item = OrderItem.objects.create(
            order=self.order,
            product=self.product,
            quantity=2,
            price=300000
        )
        self.order_item2 = OrderItem.objects.create(
            order=self.order,
            product=self.product2,
            quantity=3,
            price=250000
        )

        # Simulate what checkout has already done.
        self.product.stock = 8
        self.product2.stock = 12

        self.product.save()
        self.product2.save()

    def test_canceling_order_restores_stock(self):
        self.order.status = Order.StatusChoices.CANCELED

        admin = OrderAdmin(Order, AdminSite())

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 10)

    def test_saving_already_canceled_order_does_not_restore_stock_again(self):
        self.order.status = Order.StatusChoices.CANCELED

        admin = OrderAdmin(Order, AdminSite())

        # First cancellation restores the stock.
        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 10)

        # Save the already-canceled order again.
        self.order.refresh_from_db()

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        self.product.refresh_from_db()

        # Stock must remain 10, not become 12.
        self.assertEqual(self.product.stock, 10)


    def test_canceling_order_restores_stock_for_multiple_products(self):
        self.order.status = Order.StatusChoices.CANCELED

        admin = OrderAdmin(Order, AdminSite())

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        self.product.refresh_from_db()
        self.product2.refresh_from_db()

        self.assertEqual(self.product.stock, 10)
        self.assertEqual(self.product2.stock, 15)

    def test_canceling_confirmed_order_restores_stock(self):
        admin = OrderAdmin(Order, AdminSite())

        # Pending → Confirmed
        self.order.status = Order.StatusChoices.CONFIRMED

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        # Confirmed → Canceled
        self.order.status = Order.StatusChoices.CANCELED

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        self.product.refresh_from_db()

        self.assertEqual(self.product.stock, 10)

    def test_canceled_order_cannot_be_confirmed(self):
        admin = OrderAdmin(Order, AdminSite())

        # First cancel the order.
        self.order.status = Order.StatusChoices.CANCELED

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        # Try to confirm the canceled order.
        self.order.status = Order.StatusChoices.CONFIRMED

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.StatusChoices.CANCELED
        )

    def test_canceled_order_cannot_be_pending(self):
        admin = OrderAdmin(Order, AdminSite())

        # Cancel the order.
        self.order.status = Order.StatusChoices.CANCELED

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        # Try to change it back to Pending.
        self.order.status = Order.StatusChoices.PENDING

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.StatusChoices.CANCELED
        )

    def test_mark_selected_orders_as_confirmed(self):
        order2 = Order.objects.create(
            user=self.user,
            full_name='Jane Doe',
            phone='08098765432',
            address='456 Second Street',
            city='Abuja',
            state='FCT',
            total=300000,
            status=Order.StatusChoices.PENDING
        )

        admin = OrderAdmin(Order, AdminSite())

        queryset = Order.objects.filter(
            pk__in=[self.order.pk, order2.pk]
        )

        admin.mark_as_confirmed(
            request=None,
            queryset=queryset
        )

        self.order.refresh_from_db()
        order2.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.StatusChoices.CONFIRMED
        )

        self.assertEqual(
            order2.status,
            Order.StatusChoices.CONFIRMED
        )

    def test_mark_as_confirmed_action_is_registered(self):
        admin = OrderAdmin(Order, AdminSite())

        request = RequestFactory().get('/admin/')
        request.user = self.user

        actions = admin.get_actions(request)

        self.assertIn(
            'mark_as_confirmed',
            actions)

    def test_admin_can_bulk_confirm_orders(self):
        User = get_user_model()

        admin_user = User.objects.create_superuser(
            username='admin',
            password='adminpassword',
            email='admin@example.com'
        )

        self.client.force_login(admin_user)

        order2 = Order.objects.create(
            user=self.user,
            full_name='Jane Doe',
            phone='08098765432',
            address='456 Second Street',
            city='Abuja',
            state='FCT',
            total=300000,
            status=Order.StatusChoices.PENDING
        )

        response = self.client.post(
            '/admin/products/order/',
            {
                'action': 'mark_as_confirmed',
                '_selected_action': [
                    str(self.order.pk),
                    str(order2.pk),
                ],
            }
        )

        self.assertEqual(response.status_code, 302)

        self.order.refresh_from_db()
        order2.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.StatusChoices.CONFIRMED
        )

        self.assertEqual(
            order2.status,
            Order.StatusChoices.CONFIRMED
        )

    def test_bulk_confirm_does_not_confirm_canceled_orders(self):
        admin = OrderAdmin(Order, AdminSite())

        self.order.status = Order.StatusChoices.CANCELED

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        queryset = Order.objects.filter(pk=self.order.pk)

        admin.mark_as_confirmed(
            request=None,
            queryset=queryset
        )

        self.order.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.StatusChoices.CANCELED
        )

    def test_bulk_cancel_orders_restores_stock(self):
        admin = OrderAdmin(Order, AdminSite())

        order2 = Order.objects.create(
            user=self.user,
            full_name='Jane Doe',
            phone='08098765432',
            address='456 Second Street',
            city='Abuja',
            state='FCT',
            total=300000,
            status=Order.StatusChoices.PENDING
        )

        OrderItem.objects.create(
            order=order2,
            product=self.product,
            quantity=3,
            price=self.product.price
        )

        # Simulate stock already being reduced for order2.
        self.product.stock = 5
        self.product.save()

        queryset = Order.objects.filter(
            pk__in=[self.order.pk, order2.pk]
        )

        admin.mark_as_canceled(
            request=None,
            queryset=queryset
        )

        self.order.refresh_from_db()
        order2.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.StatusChoices.CANCELED
        )

        self.assertEqual(
            order2.status,
            Order.StatusChoices.CANCELED
        )

        self.assertEqual(
            self.product.stock,
            10
        )

    def test_bulk_cancel_does_not_restore_stock_twice(self):
        admin = OrderAdmin(Order, AdminSite())

        # Cancel the order for the first time.
        self.order.status = Order.StatusChoices.CANCELED

        admin.save_model(
            request=None,
            obj=self.order,
            form=None,
            change=True
        )

        self.product.refresh_from_db()
        stock_after_first_cancel = self.product.stock

            # Try to cancel the same order again.
        queryset = Order.objects.filter(pk=self.order.pk)

        admin.mark_as_canceled(
            request=None,
            queryset=queryset
        )

        self.product.refresh_from_db()

        self.assertEqual(
            self.product.stock,
            stock_after_first_cancel
        )

    def test_mark_as_canceled_action_is_registered(self):
        admin = OrderAdmin(Order, AdminSite())

        request = RequestFactory().get('/admin/')
        request.user = self.user

        actions = admin.get_actions(request)

        self.assertIn(
            'mark_as_canceled',
            actions
        )

    def test_admin_can_bulk_cancel_orders(self):
        User = get_user_model()

        admin_user = User.objects.create_superuser(
            username='admin_cancel',
            password='adminpassword',
            email='admin_cancel@example.com'
        )

        self.client.force_login(admin_user)

        queryset = Order.objects.filter(pk=self.order.pk)

        response = self.client.post(
            '/admin/products/order/',
            {
                'action': 'mark_as_canceled',
                '_selected_action': [str(self.order.pk)],
            }
        )

        self.assertEqual(response.status_code, 302)

        self.order.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(
            self.order.status,
            Order.StatusChoices.CANCELED
        )

class ProductAdminTest(TestCase):

    def setUp(self):
        self.category = Category.objects.create(
            name='Phones'
        )

        self.product = Product.objects.create(
            name='iPhone 14',
            description='Apple smartphone',
            price=300000,
            stock=8,
            category=self.category
        )

        self.admin = ProductAdmin(
            Product,
            AdminSite()
        )

    def test_stock_is_displayed_in_admin_list(self):
        self.assertIn(
            'stock',
            self.admin.list_display
        )
    
    # def test_low_stock_is_detected(self):
    #     self.product.stock = 3
    #     self.product.save()

    #     self.assertTrue(
    #         self.admin.is_low_stock(self.product)
    #     )
        
    # def test_normal_stock_is_not_low_stock(self):
    #     self.product.stock = 10
    #     self.product.save()

    #     self.assertFalse(
    #         self.admin.is_low_stock(self.product)
    #     )

    # def test_low_stock_is_displayed_in_admin_list(self):
    #     self.assertIn(
    #         'is_low_stock',
    #         self.admin.list_display
    #     )
    def test_stock_status_filter_out_of_stock(self):
        Product.objects.create(
            name='Out of Stock Phone',
            description='No stock',
            price=200000,
            stock=0,
            category=self.category,
        )

        Product.objects.create(
            name='Available Phone',
            description='Available',
            price=250000,
            stock=10,
            category=self.category,
        )

        request = RequestFactory().get(
            '/admin/products/product/',
            {'stock_status': 'out_of_stock'}
        )

        filter_instance = StockStatusFilter(
                            request,
                            request.GET.copy(), #query dict is immutable. we need a copy of it if we are going to pop items from the dic
                            Product,
                            self.admin
                        )
        queryset = filter_instance.queryset(
            request,
            Product.objects.all()
        )

        self.assertTrue(queryset.exists())

        self.assertFalse(
            queryset.filter(stock__gt=0).exists())