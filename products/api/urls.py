from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from rest_framework.routers import DefaultRouter





urlpatterns = [
    path('products/', views.ProductListCreateAPIView.as_view()),
    path('products/<int:pk>/', views.ProductDetailAPIView.as_view()),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
   
]

router = DefaultRouter()
router.register('orders', views.OrderViewSet, basename='order')
urlpatterns += router.urls
