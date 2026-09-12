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


class ProductListCreateAPIView(generics.ListCreateAPIView):
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]



class ProductDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.request.method in  ['PUT', 'DELETE', 'PATCH']:
            return [IsAdminUser()]
        return [AllowAny()]

    

class OrderViewSet(viewsets.ModelViewSet):
    
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]


    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user).prefetch_related(
            'items__product')



    



    
    
    


