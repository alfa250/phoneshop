from rest_framework.response import Response
from rest_framework.views import APIView
from products.models import Product, Order, OrderItem
from rest_framework import generics
from .serializers import ProductSerializer, OrderSerializer, OrderItemSerializer
from rest_framework.generics import RetrieveAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework.permissions import IsAdminUser, AllowAny, IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework import filters, generics, viewsets
from django.core.cache import cache
from rest_framework.response import Response
from .throttles import ProductThrottle



class ProductListCreateAPIView(generics.ListCreateAPIView):
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    throttle_classes = [ProductThrottle]
    
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]

    def list(self, request, *args, **kwargs):
        cache_key = 'product_list'
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 5)  # Cache for 5 minutes
        return response

    
    def perform_create(self, serializer):
        serializer.save()
        cache.delete('product_list')  # Clear the cache when a new product is created



class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in  ['PUT', 'DELETE', 'PATCH']:
            return [IsAdminUser()]
        return [AllowAny()]

    def retrieve(self, request, *args, **kwargs):
        product_id = kwargs['pk']
        cache_key = f'product_{product_id}'
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)
        response = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 5)  # Cache for 5 minutes
        return response
    
    def perform_update(self, serializer):
        serializer.save()
        cache.delete('product_list')
        product_id = serializer.instance.id
        cache.delete(f'product_{product_id}')  # Clear the cache for the updated product
    
    def perform_destroy(self, instance):
        product_id = instance.id
        instance.delete()
        cache.delete('product_list')
        cache.delete(f'product_{product_id}')  # Clear the cache for the deleted product

        

    

class OrderViewSet(viewsets.ModelViewSet):
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user).prefetch_related(
            'items__product')



    



    
    
    


