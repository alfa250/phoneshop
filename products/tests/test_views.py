from django.test import TestCase
from django.urls import reverse
from products.models import Product, Order, OrderItem
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model


class ProductListViewTest(TestCase):

    def test_product_list_view_loads(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)


    def test_product_list_view_returns_products(self):
        product = Product.objects.create(
            name = 'iphone 14',
            description = 'a powerful smartphone',
            price = 150000,
            stock = 10
        )

        response = self.client.get(reverse('home'))

        self.assertIn(product, 
        response.context['products'])

    def test_product_list_search_filters_products(self):
        samsung = Product.objects.create(
            name = 'samsung galaxy s24',
            description = 'A samsung smartphone',
            price = 500000,
            stock = 10

        )

        iphone = Product.objects.create(
            name = 'iphone 14',
            description = 'An apple smartphone',
            price = 3000000,
            stock = 10
        )

        response = self.client.get(reverse('home'), {'search':'samsung'})

        self.assertIn(samsung, response.context['products'])

        self.assertNotIn(iphone, response.context['products'])


    def test_product_list_search_returns_no_products_when_no_match(self):

        samsung = Product.objects.create(
            name = 'samsung galaxy s24',
            description = 'A samsung smartphone',
            price = 500000,
            stock = 10

        )
        response = self.client.get(reverse('home'), {'search':'nokia'})
        self.assertEqual(response.context['products'].count(), 0)
 
    def test_product_list_search_is_case_insensitive(self):

        samsung = Product.objects.create(
            name = 'SAMSUNG galaxy s24',
            description = 'A samsung smartphone',
            price = 500000,
            stock = 10

        )

        response = self.client.get(
            reverse('home'),
            {'search':'samsung'}
        )

        self.assertIn(samsung, response.context['products'])

class ProductDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username = 'testuser',
            password = 'strongpassword123'
        )

    def test_product_detail_view_loads(self):
        product = Product.objects.create(
            name = 'iphone 14',
            description = 'An apple smartphone',
            price = 3000000,
            stock = 10)

        self.client.login(
            username = 'testuser',
            password = 'strongpassword123'
        )


        response = self.client.get(reverse('product_detail', kwargs = {'pk': product.pk}))
        
        self.assertEqual(response.status_code, 200)

    def test_product_detail_view_returns_correct_product(self):
        product = Product.objects.create(
            name = 'iphone 14',
            description = 'An apple smartphone',
            price = 3000000,
            stock = 10)

        self.client.force_login(self.user)

        response = self.client.get(reverse(
            'product_detail',
            kwargs = {'pk':product.pk}
        ))

        self.assertEqual(response.context['product'], product)

    def test_product_detail_view_returns_404_for_nonexistent_product(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse(
            'product_detail', kwargs = {'pk': 999999}
        ))

        self.assertEqual(response.status_code, 404)

class AddToCartViewTest(TestCase):

    def test_add_product_to_cart(self):
        
        product = Product.objects.create(
            name = 'iphone 14',
            description = 'An apple smartphone',
            price = 3000000,
            stock = 10)

        response = self.client.post(
            reverse(
                'add_to_cart',
                kwargs = {'product_id': product.pk}
            )
        )

        cart = self.client.session.get('cart')

        self.assertIn(str(product.id), cart)

        self.assertEqual(cart[str(product.pk)], 1)

    def test_add_same_product_to_cart_increases_quantity(self):
        product = Product.objects.create(
            name = 'iphone 14',
            description = 'An apple smartphone',
            price = 3000000,
            stock = 10)
        
        self.client.post(reverse(
            'add_to_cart', 
            kwargs = {'product_id':product.id}
        ))

        self.client.post(reverse(
            'add_to_cart', 
            kwargs = {'product_id':product.id}
        ))
        
        cart = self.client.session.get('cart')

        self.assertEqual(cart[str(product.id)], 2)

    def test_add_different_products_to_cart(self):
        product1 = Product.objects.create(
            name = 'iphone 14',
            description = 'An apple smartphone',
            price = 3000000,
            stock = 10)
        
        product2 = Product.objects.create(
            name = 'SAMSUNG galaxy s24',
            description = 'A samsung smartphone',
            price = 500000,
            stock = 10

        )

        self.client.post(
            reverse(
                'add_to_cart',
                kwargs = {'product_id':product1.id}
            )
        )

        self.client.post(
            reverse(
                'add_to_cart',
                kwargs = {'product_id':product2.id}
            )
        )

        cart = self.client.session.get('cart')

        self.assertIn(str(product1.id), cart)
        self.assertIn(str(product2.id), cart)

        self.assertEqual(cart[str(product1.id)], 1)
        self.assertEqual(cart[str(product2.id)], 1)


    def test_remove_product_from_cart(self):
        
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        self.client.post(
            reverse(
                'add_to_cart',
                kwargs={'product_id': product.id}
            )
        )

        response = self.client.post(
            reverse(
                'remove_from_cart',
                kwargs={'product_id': product.pk}
            )
        )

        cart = self.client.session.get('cart')

        self.assertNotIn(str(product.pk), cart)
        self.assertRedirects(response, reverse('cart'))

    def test_update_product_quantity_in_cart(self):

        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        self.client.post(
            reverse(
                'add_to_cart',
                kwargs = {'product_id':product.id}
            )
        )
        response = self.client.post(
            reverse(
                'update_cart',
                kwargs = {
                    'product_id':product.id
                }
            ),
            data = {'quantity':5}
        )


        cart = self.client.session.get('cart')

        self.assertEqual(cart[str(product.id)], 5)
        self.assertRedirects(response, reverse('cart'))

    def test_update_cart_does_not_exceed_stock(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        self.client.post(reverse(
            'add_to_cart',
            kwargs = {'product_id':product.id}
        ))

        response = self.client.post(
            reverse(
                'update_cart',
                kwargs = {'product_id': product.id}
            ),
            data = {'quantity':15}
        )


        cart = self.client.session.get('cart')

        self.assertEqual(cart[str(product.id)], 10)
        self.assertRedirects(response, reverse('cart'))


    def test_update_cart_removes_product_when_quantity_is_zero(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )
        self.client.post(reverse(
            'add_to_cart',
            kwargs = {'product_id':product.id}
        ))
        response = self.client.post(
            reverse(
                'update_cart',
                kwargs = {'product_id': product.id}
            ),
            data = {'quantity':0}
        )

        cart = self.client.session.get('cart')

        self.assertNotIn(str(product.pk), cart)
        self.assertRedirects(response, reverse('cart'))

    

    def test_update_cart_when_product_not_in_cart(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )
        response = self.client.post(
            reverse(
                'update_cart',
                kwargs = {'product_id': product.id}
            ),
            data = {'quantity':5}
        )

        cart = self.client.session.get('cart', {})

        self.assertNotIn(str(product.pk), cart)
        self.assertRedirects(response, reverse('cart'))

    def test_cart_view_loads_cart_items(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )
        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        response = self.client.get(reverse('cart'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, product.name)

    def test_cart_view_calculates_total(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )
        session = self.client.session
        session['cart'] = {
            str(product.id):2
        }

        session.save()

        response = self.client.get(reverse('cart'))

        self.assertEqual(response.context['total'], 6000000)

    def test_cart_view_calculates_item_subtotal(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.id):2
        }
        session.save()

        response = self.client.get(reverse('cart'))

        cart_items = response.context['cart_items']

        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['quantity'], 2)
        self.assertEqual(cart_items[0]['price'], product.current_price)
        self.assertEqual(cart_items[0]['subtotal'], product.current_price * 2)


    def test_cart_view_calculates_total_for_multiple_products(self):
        product1 = Product.objects.create(
        name='iphone 14',
        description='An apple smartphone',
        price=3000000,
        stock=10
        )

        product2 = Product.objects.create(
            name='Samsung S24',
            description='A Samsung smartphone',
            price=2500000,
            stock=10
        )
        session = self.client.session
        session['cart'] = {
            str(product1.id):2,
            str(product2.id):1
        }
        session.save()

        response = self.client.get(reverse('cart'))

        cart_items = response.context['cart_items']

        self.assertEqual(len(cart_items), 2)
        self.assertEqual(response.context['total'], 8500000)


    def test_cart_view_skips_deleted_product(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        product.delete()

        response = self.client.get(reverse('cart'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart_items'], [])
        self.assertEqual(response.context['total'], 0)

    def test_cart_view_with_empty_cart(self):
        response = self.client.get(reverse('cart'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart_items'], [])
        self.assertEqual(response.context['total'], 0)        

class CheckoutViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        self.client.login(
            username='testuser',
            password='testpassword123'
        )
    def test_checkout_creates_order(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        self.client.post(
            reverse(
                'add_to_cart',
                kwargs={'product_id': product.pk}
            )
        )

        response = self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        self.assertEqual(Order.objects.count(), 1)

        order = Order.objects.first()

        self.assertEqual(order.user, self.user)
        self.assertEqual(order.full_name, 'Aondofa Alfred')
        self.assertEqual(order.phone, '08012345678')
        self.assertEqual(order.address, '123 Main Street')
        self.assertEqual(order.city, 'Abuja')
        self.assertEqual(order.state, 'FCT')

    def test_checkout_creates_order_item(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        self.assertEqual(OrderItem.objects.count(), 1)

        order_item = OrderItem.objects.first()

        self.assertEqual(order_item.product, product)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, product.current_price)
        

    def test_checkout_calculates_order_total(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        order = Order.objects.first()

        self.assertEqual(order.total, 6000000)

    def test_checkout_reduces_product_stock(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        product.refresh_from_db()

        self.assertEqual(product.stock, 8)


    def test_checkout_clears_cart(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        cart = self.client.session.get('cart')

        self.assertEqual(cart, {})

    def test_checkout_with_empty_cart_does_not_create_order(self):
        response = self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Your cart is empty.')

    def test_checkout_fails_when_stock_is_insufficient(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=5
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 8
        }
        session.save()

        response = self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

        self.assertIn(
        'Not enough stock for iphone 14. Available: 5, requested: 8.',
        response.context['form'].non_field_errors()
        )

    def test_checkout_does_not_reduce_stock_when_stock_is_insufficient(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=5
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 8
        }
        session.save()

        self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        product.refresh_from_db()

        self.assertEqual(product.stock, 5)


    def test_checkout_keeps_cart_when_stock_is_insufficient(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=5
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 8
        }
        session.save()

        self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        cart = self.client.session.get('cart', {})

        self.assertEqual(cart[str(product.pk)], 8)

    def test_checkout_fails_when_product_does_not_exist(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 1
        }
        session.save()

        product_id = product.pk
        product.delete()

        response = self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        self.assertEqual(Order.objects.count(), 0)
        self.assertEqual(response.status_code, 200)

    def test_checkout_redirects_to_order_success(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 1
        }
        session.save()

        response = self.client.post(
            reverse('checkout'),
            data={
                'full_name': 'Aondofa Alfred',
                'phone': '08012345678',
                'address': '123 Main Street',
                'city': 'Abuja',
                'state': 'FCT',
            }
        )

        self.assertRedirects(
            response,
            reverse('order_success')
        )


class OrderSuccessViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        self.client.login(
            username='testuser',
            password='testpassword123'
        )

    def test_order_success_displays_order(self):
        order = Order.objects.create(
            user=self.user,
            full_name='Aondofa Alfred',
            phone='08012345678',
            address='123 Main Street',
            city='Abuja',
            state='FCT',
            total=6000000
        )

        session = self.client.session
        session['order_id'] = str(order.order_id)
        session.save()

        response = self.client.get(reverse('order_success'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'], order)

        
    def test_order_success_without_order_id(self):
        response = self.client.get(
            reverse('order_success')
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn('order', response.context)

    def test_order_success_does_not_show_another_users_order(self):
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='otherpassword123'
        )

        order = Order.objects.create(
            user=other_user,
            full_name='Other User',
            phone='08098765432',
            address='456 Other Street',
            city='Lagos',
            state='Lagos',
            total=5000000
        )

        session = self.client.session
        session['order_id'] = str(order.order_id)
        session.save()

        response = self.client.get(
            reverse('order_success')
        )

        self.assertEqual(response.status_code, 404)


    def test_order_success_with_invalid_order_id(self):
        session = self.client.session
        session['order_id'] = '00000000-0000-0000-0000-000000000000'
        session.save()

        response = self.client.get(
            reverse('order_success')
        )

        self.assertEqual(response.status_code, 404)

class MyOrdersViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        self.client.login(
            username='testuser',
            password='testpassword123'
        )

    def test_my_orders_view_displays_users_orders(self):
        order = Order.objects.create(
            user=self.user,
            full_name='Aondofa Alfred',
            phone='08012345678',
            address='123 Main Street',
            city='Abuja',
            state='FCT',
            total=6000000
        )

        response = self.client.get(
            reverse('my_orders')
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(order, response.context['orders'])

    def test_my_orders_view_does_not_show_other_users_orders(self):
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='otherpassword123'
        )

        other_order = Order.objects.create(
            user=other_user,
            full_name='Other User',
            phone='08098765432',
            address='456 Other Street',
            city='Lagos',
            state='Lagos',
            total=5000000
        )

        response = self.client.get(
            reverse('my_orders')
        )

        self.assertNotIn(
            other_order,
            response.context['orders']
        )

    def test_my_orders_view_orders_are_newest_first(self):
        older_order = Order.objects.create(
            user=self.user,
            full_name='Aondofa Alfred',
            phone='08012345678',
            address='123 Old Street',
            city='Abuja',
            state='FCT',
            total=3000000
        )

        newer_order = Order.objects.create(
            user=self.user,
            full_name='Aondofa Alfred',
            phone='08012345678',
            address='123 New Street',
            city='Abuja',
            state='FCT',
            total=5000000
        )

        response = self.client.get(
            reverse('my_orders')
        )

        orders = list(response.context['orders'])

        self.assertEqual(orders[0], newer_order)
        self.assertEqual(orders[1], older_order)

    def test_my_orders_view_requires_login(self):
        self.client.logout()

        response = self.client.get(
            reverse('my_orders')
        )

        self.assertEqual(response.status_code, 302)

class OrderDetailViewTest(TestCase):

    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpassword123'
        )

        self.client.login(
            username='testuser',
            password='testpassword123'
        )

    def test_order_detail_displays_users_order(self):
        order = Order.objects.create(
            user=self.user,
            full_name='Aondofa Alfred',
            phone='08012345678',
            address='123 Main Street',
            city='Abuja',
            state='FCT',
            total=6000000
        )

        response = self.client.get(
            reverse(
                'order_detail',
                kwargs={'pk': order.pk}
            )
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['order'], order)

    def test_order_detail_does_not_show_another_users_order(self):
        other_user = get_user_model().objects.create_user(
            username='otheruser',
            password='otherpassword123'
        )

        other_order = Order.objects.create(
            user=other_user,
            full_name='Other User',
            phone='08098765432',
            address='456 Other Street',
            city='Lagos',
            state='Lagos',
            total=5000000
        )

        response = self.client.get(
            reverse(
                'order_detail',
                kwargs={'pk': other_order.pk}
            )
        )

        self.assertEqual(response.status_code, 404)


    def test_order_detail_with_invalid_order_id(self):
        response = self.client.get(
            reverse(
                'order_detail',
                kwargs={
                    'pk': '00000000-0000-0000-0000-000000000000'
                }
            )
        )

        self.assertEqual(response.status_code, 404)

    def test_order_detail_requires_login(self):
        order = Order.objects.create(
            user=self.user,
            full_name='Aondofa Alfred',
            phone='08012345678',
            address='123 Main Street',
            city='Abuja',
            state='FCT',
            total=6000000
        )

        self.client.logout()

        response = self.client.get(
            reverse(
                'order_detail',
                kwargs={'pk': order.pk}
            )
        )

        self.assertEqual(response.status_code, 302)



class CartViewTest(TestCase):

    def test_cart_view_with_empty_cart(self):
        response = self.client.get(
            reverse('cart')
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart_items'], [])
        self.assertEqual(response.context['total'], 0)

    def test_cart_view_displays_product_in_cart(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        response = self.client.get(
            reverse('cart')
        )

        self.assertEqual(response.status_code, 200)

        cart_items = response.context['cart_items']

        self.assertEqual(len(cart_items), 1)
        self.assertEqual(cart_items[0]['product'], product)

    def test_cart_view_displays_correct_quantity(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 3
        }
        session.save()

        response = self.client.get(
            reverse('cart')
        )

        cart_items = response.context['cart_items']

        self.assertEqual(cart_items[0]['quantity'], 3)       
            
    def test_cart_view_calculates_correct_subtotal(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 3
        }
        session.save()

        response = self.client.get(
            reverse('cart')
        )

        cart_items = response.context['cart_items']

        self.assertEqual(
            cart_items[0]['subtotal'],
            9000000
        )

    def test_cart_view_calculates_correct_total(self):
        iphone = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        samsung = Product.objects.create(
            name='Samsung S23',
            description='A Samsung smartphone',
            price=2000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(iphone.pk): 2,
            str(samsung.pk): 3,
        }
        session.save()

        response = self.client.get(
            reverse('cart')
        )

        self.assertEqual(
            response.context['total'],
            12000000
        )

    def test_cart_view_skips_deleted_product(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        product.delete()

        response = self.client.get(
            reverse('cart')
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['cart_items'], [])
        self.assertEqual(response.context['total'], 0)

    def test_cart_view_displays_correct_price(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 1
        }
        session.save()

        response = self.client.get(
            reverse('cart')
        )

        cart_items = response.context['cart_items']

        self.assertEqual(
            cart_items[0]['price'],
            product.current_price
        )

class RemoveFromCartViewTest(TestCase):

    def test_remove_product_from_cart(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        response = self.client.post(
            reverse(
                'remove_from_cart',
                kwargs={'product_id': product.pk}
            )
        )

        cart = self.client.session.get('cart', {})

        self.assertNotIn(str(product.pk), cart)
        self.assertRedirects(response, reverse('cart'))

    def test_remove_product_not_in_cart(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        response = self.client.post(
            reverse(
                'remove_from_cart',
                kwargs={'product_id': product.pk}
            )
        )

        cart = self.client.session.get('cart', {})

        self.assertNotIn(str(product.pk), cart)
        self.assertRedirects(response, reverse('cart'))


class UpdateCartViewTest(TestCase):

    def test_update_cart_changes_quantity(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 1
        }
        session.save()

        response = self.client.post(
            reverse(
                'update_cart',
                kwargs={'product_id': product.pk}
            ),
            {'quantity': 5}
        )

        cart = self.client.session.get('cart', {})

        self.assertEqual(
            cart[str(product.pk)],
            5
        )

        self.assertRedirects(
            response,
            reverse('cart')
        )

    def test_update_cart_removes_product_when_quantity_is_less_than_one(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        response = self.client.post(
            reverse(
                'update_cart',
                kwargs={'product_id': product.pk}
            ),
            {'quantity': 0}
        )

        cart = self.client.session.get('cart', {})

        self.assertNotIn(
            str(product.pk),
            cart
        )

        self.assertRedirects(
            response,
            reverse('cart')
        )

    def test_update_cart_limits_quantity_to_available_stock(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=5
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        response = self.client.post(
            reverse(
                'update_cart',
                kwargs={'product_id': product.pk}
            ),
            {'quantity': 8}
        )

        cart = self.client.session.get('cart', {})

        self.assertEqual(
            cart[str(product.pk)],
            5
        )

        self.assertRedirects(
            response,
            reverse('cart')
        )

    def test_update_cart_shows_stock_warning(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=5
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        response = self.client.post(
            reverse(
                'update_cart',
                kwargs={'product_id': product.pk}
            ),
            {'quantity': 8}
        )

        messages = list(response.wsgi_request._messages)

        self.assertEqual(
            str(messages[0]),
            'Only 5 units of iphone 14 are available.'
        )

    def test_update_cart_product_not_in_cart(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        response = self.client.post(
            reverse(
                'update_cart',
                kwargs={'product_id': product.pk}
            ),
            {'quantity': 5}
        )

        cart = self.client.session.get('cart', {})

        self.assertNotIn(
            str(product.pk),
            cart
        )

        self.assertRedirects(
            response,
            reverse('cart')
        )

    def test_update_cart_handles_invalid_quantity(self):
        product = Product.objects.create(
            name='iphone 14',
            description='An apple smartphone',
            price=3000000,
            stock=10
        )

        session = self.client.session
        session['cart'] = {
            str(product.pk): 2
        }
        session.save()

        response = self.client.post(
            reverse(
                'update_cart',
                kwargs={'product_id': product.pk}
            ),
            {'quantity': 'abc'}
        )

        self.assertEqual(response.status_code, 302)








        

        
        





        



    








 










