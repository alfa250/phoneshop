
from django.views.generic import ListView, DetailView
from .models import Product, Order, OrderItem
from django.contrib.auth.views import LoginView, LogoutView
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



class ProductListView(ListView):
    model = Product
    template_name = 'home.html'
    context_object_name = 'products'

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

    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'You have successfully logged out.')
        return super().dispatch(request, *args, **kwargs)
    
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

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "product_detail.html"
    context_object_name = "product"
    login_url = 'login'
    

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

                subtotal = product.price * quantity

                total += subtotal

                cart_items.append({
                    "product": product,
                    "quantity": quantity,
                    "subtotal": subtotal,
                })

            except Product.DoesNotExist:
                continue

        context["cart_items"] = cart_items
        context["total"] = total

        return context