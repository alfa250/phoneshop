from django.db import transaction
from django.views.generic import ListView, DetailView
from .models import Product, Order, OrderItem, Category
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.edit import CreateView, FormView
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView
from .forms import RegisterForm
from django.shortcuts import get_object_or_404, redirect
from django.views import View
from django.views.generic import RedirectView
from django.views.generic import DetailView
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect



class ProductListView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

    def get_queryset(self):
        queryset = Product.objects.all()

        search = self.request.GET.get('search', '').strip()

        if search:
            queryset = queryset.filter(
                name__icontains=search
            )
        return queryset

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "product_detail.html"
    context_object_name = "product"
    login_url = 'login'

        
class LoginUserView(LoginView):
    template_name = 'login.html'

    def form_valid(self, form):
        messages.success(self.request, 'You have successfully logged in.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Invalid username or password.')
        return super().form_invalid(form)

class LogoutUserView(LogoutView):
    next_page = 'login'

    def dispatch(self, *args, **kwargs):
        messages.success(self.request, 'You have successfully logged out.')
        return super().dispatch(self.request, *args, **kwargs)
    
class RegisterUserView(CreateView):
    form_class = RegisterForm
    template_name = 'register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        messages.success(self.request, 'Account created successfully. Please log in.')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)


    



class CategoryListView(ListView):
    model = Category
    template_name = 'categories.html'
    context_object_name = 'categories'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context["categories"])
        return context


class CategoryProductsView(ListView):
    model = Product
    template_name = "category_products.html"
    context_object_name = "products"

    def get_queryset(self):
        self.category = Category.objects.get(pk=self.kwargs["pk"])
        return Product.objects.filter(category=self.category)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category"] = self.category
        return context


class CartView(TemplateView):
    template_name = "cart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        cart = self.request.session.get("cart", {})

        cart_items = []
        total = 0

        for product_id, quantity in cart.items():

            try:
                product = Product.objects.get(pk=product_id)
            except Product.DoesNotExist:
                continue
            price = product.current_price
            subtotal = price * quantity

            total += subtotal

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "price": price,
                "subtotal": subtotal,
            })

            

        context["cart_items"] = cart_items
        context["total"] = total

        return context

class AddToCartView(View):

    pattern_name = "home"

    def post(self, request, *args, **kwargs):

        product = get_object_or_404(Product, pk=kwargs["product_id"])

        cart = request.session.get("cart", {})

        product_id = str(product.id)

        cart[product_id] = cart.get(product_id, 0) + 1

        request.session["cart"] = cart
        request.session.modified = True

        messages.success(
            request,
            f"{product.name} added to cart."
        )

        return redirect('home')




class RemoveFromCartView(View):
    def post(self, request, product_id):
        cart = request.session.get("cart", {})
        product_id = str(product_id)
        if product_id in cart:
            del cart[product_id]
            request.session["cart"] = cart
            request.session.modified = True
            messages.success(request, "Item removed from cart.")
        return redirect("cart")


class UpdateCartView(View):

    def post(self, request, product_id):

        cart = request.session.get("cart", {})

        product_id = str(product_id)

        if product_id not in cart:
            return redirect("cart")

        product = get_object_or_404(Product, pk=product_id)
        try:
            quantity = int(request.POST.get("quantity", 1))
        except (TypeError, ValueError):
            messages.warning(
                request,
                "Please enter a valid quantity."
            )
            return redirect("cart")

        # Prevent invalid quantities
        if quantity < 1:
            del cart[product_id]

        # Don't allow the customer to exceed available stock
        elif quantity > product.stock:
            messages.warning(
                request,
                f"Only {product.stock} units of {product.name} are available."
            )
            cart[product_id] = product.stock

        else:
            cart[product_id] = quantity

        request.session["cart"] = cart
        request.session.modified = True

        return redirect("cart")



class CheckoutView(LoginRequiredMixin, FormView):


    template_name = 'checkout.html'
    form_class = CheckoutForm
    success_url = reverse_lazy('order_success')

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        cart = self.request.session.get('cart', {})

        cart_items = []
        total = 0

        for product_id, quantity in cart.items():

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                continue

            subtotal = product.current_price * quantity

            cart_items.append({
                'product': product,
                'quantity': quantity,
                'subtotal': subtotal,
            })

            total += subtotal

        context['cart_items'] = cart_items
        context['total'] = total

        return context

    @transaction.atomic
    def form_valid(self, form):

        cart = self.request.session.get('cart', {})

        if not cart:
            form.add_error(None, 'Your cart is empty.')
            return self.form_invalid(form)

        total = 0
        order_items = []

        # 1. Validate products and stock
        for product_id, quantity in cart.items():

            try:
                product = Product.objects.get(id=product_id)
            except Product.DoesNotExist:
                form.add_error(
                    None,
                    f'Product {product_id} does not exist.'
                )
                return self.form_invalid(form)

            # 2. Check stock
            if product.stock < quantity:
                form.add_error(
                    None,
                    f'Not enough stock for {product.name}. '
                    f'Available: {product.stock}, requested: {quantity}.'
                )
                return self.form_invalid(form)

            # 3. Capture the current price
            price = product.current_price

            # 4. Calculate subtotal
            subtotal = price * quantity

            # 5. Add to total
            total += subtotal

            # 6. Store information temporarily
            order_items.append({
                'product': product,
                'quantity': quantity,
                'price': price,
            })

        # 7. Create the Order
        order = Order.objects.create(
            user=self.request.user,
            full_name=form.cleaned_data['full_name'],
            phone=form.cleaned_data['phone'],
            address=form.cleaned_data['address'],
            city=form.cleaned_data['city'],
            state=form.cleaned_data['state'],
            total=total,
        )

        # 8. Create OrderItems and reduce stock
        for item in order_items:

            OrderItem.objects.create(
                order=order,
                product=item['product'],
                quantity=item['quantity'],
                price=item['price'],
            )

            product = item['product']
            product.stock -= item['quantity']
            product.save(update_fields=['stock'])

        # 9. Clear the cart
        self.request.session['cart'] = {}

        # 10. Store order ID in session
        self.request.session['order_id'] = str(order.order_id)

        self.request.session.modified = True

        return super().form_valid(form)


class OrderSuccessView(LoginRequiredMixin, TemplateView):

    template_name = 'order_success.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        order_id = self.request.session.get('order_id')

        if order_id:
            order = get_object_or_404(
                Order,
                order_id=order_id,
                user=self.request.user
            )

            context['order'] = order

        return context


class MyOrdersView(LoginRequiredMixin, ListView):

    model = Order
    template_name = 'my_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
            ).order_by('-date_created')

        
class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'order_detail.html'
    context_object_name = 'order'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


