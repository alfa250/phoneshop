from django.urls import path
from django.urls import include
from . import views



urlpatterns = [
    path('', views.ProductListView.as_view(), name = 'home'),
    path('login/', views.LoginUserView.as_view(), name = 'login'),
    path('logout/', views.LogoutUserView.as_view(), name = 'logout'),
    path('register/', views.RegisterUserView.as_view(), name = 'register'),
    path('add-to-cart/<int:product_id>/', views.AddToCartView.as_view(), name='add_to_cart'),
    path('product/<int:pk>/', views.ProductDetailView.as_view(), name='product_detail'),
    path('cart/', views.CartView.as_view(), name='cart'),
    path('categories/', views.CategoryListView.as_view(), name='categories'),
    path('categories/<int:pk>/', views.CategoryProductsView.as_view(), name='category_products'),
    path('checkout/', views.CheckoutView.as_view(), name='checkout'),
    path('order-success/', views.OrderSuccessView.as_view(), name='order_success'),
    path('my-orders/', views.MyOrdersView.as_view(), name='my_orders'),
    path('order/<uuid:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
]

