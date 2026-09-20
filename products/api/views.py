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
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import (extend_schema, 
                                    OpenApiParameter, 
                                    OpenApiExample, 
                                    OpenApiResponse,
                                    extend_schema_view)


@extend_schema_view(
    get=extend_schema(
        description="Retrieve a list of products.",

        parameters=[
            OpenApiParameter(
                name='category',
                description='Filter products by category ID.',
                required=False,
                type=int,
            ),
            OpenApiParameter(
                name='is_sale',
                description='Filter products by sale status.',
                required=False,
                type=bool,
            ),
            OpenApiParameter(
                name='search',
                description='Search products by name or description.',
                required=False,
                type=str,
            ),
            OpenApiParameter(
                name='ordering',
                description='Order products by name, price, or stock. Use - for descending order.',
                required=False,
                type=str,
            ),
        ],

        responses={
            200: ProductSerializer(many=True),
            429: OpenApiResponse(
                description='Request was throttled. Try again later.'
            ),
        },

        examples=[
            OpenApiExample(
                'Product list example',
                summary='Example product list',
                description='Example response containing products.',
                value=[
                    {
                        'id': 1,
                        'name': 'iPhone 14',
                        'description': 'Apple smartphone with 128GB storage.',
                        'price': '300000.00',
                        'sale_price': '280000.00',
                        'is_sale': True,
                        'stock': 10,
                        'category': 3,
                        'current_price': '280000.00'
                    },
                    {
                        'id': 2,
                        'name': 'Test Phone',
                        'description': 'A sample smartphone.',
                        'price': '100.00',
                        'sale_price': None,
                        'is_sale': False,
                        'stock': 5,
                        'category': 1,
                        'current_price': '100.00'
                    }
                ],
                response_only=True,
            )
        ],
    ),

    post=extend_schema(
        description="Create a new product. Admin access is required.",

        request=ProductSerializer,

        responses={
            201: ProductSerializer,
            400: OpenApiResponse(
                description='Invalid product data.'
            ),
            403: OpenApiResponse(
                description='Admin access required.'
            ),
            429: OpenApiResponse(
                description='Request was throttled. Try again later.'
            ),
        },

        examples=[
            OpenApiExample(
                'Product creation example',
                summary='Example product',
                description='Example request for creating a product.',
                value={
                    'name': 'iPhone 14',
                    'description': 'Apple smartphone with 128GB storage.',
                    'price': '300000.00',
                    'sale_price': '280000.00',
                    'is_sale': True,
                    'stock': 10,
                    'category': 3
                },
                request_only=True,
            )
        ],
    ),
)
class ProductListCreateAPIView(generics.ListCreateAPIView):
    
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    throttle_classes = [ProductThrottle]
    
    
    filterset_fields = ['category', 'is_sale']
    filter_backends = [DjangoFilterBackend,
                        SearchFilter, 
                        OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['price', 'stock', 'name']

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAdminUser()]
        return [AllowAny()]
    
    def list(self, request, *args, **kwargs):
        cache_key = f"product_list_{request.get_full_path()}"

        #cache_key = 'product_list'
        cached_response = cache.get(cache_key)
        if cached_response:
            return Response(cached_response)
        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 60 * 5)  # Cache for 5 minutes
        return response

    
    def perform_create(self, serializer):
        serializer.save()
        cache.clear()  # Clear the cache when a new product is created



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

        

    
@extend_schema_view(
    list=extend_schema(
        description="Retrieve the authenticated user's orders.",
        responses={
        200: OrderSerializer(many=True),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
    },
    ),

    retrieve=extend_schema(
        description="Retrieve a specific order belonging to the authenticated user.",
        responses={
        200: OrderSerializer,
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(
            description="Order not found."
        ),
    },
        examples=[
            OpenApiExample(
                'Order response example',
                summary='Example order response',
                description='Example response returned when retrieving an order.',
                value={
                    'user': 1,
                    'order_id': '550e8400-e29b-41d4-a716-446655440000',
                    'status': 'Pending',
                    'items': [
                        {
                            'product': 1,
                            'product_name': 'Test Phone',
                            'product_price': '100.00',
                            'quantity': 2,
                            'subtotal': '200.00'
                        }
                    ],
                    'total_price': '200.00',
                    'state': 'FCT',
                    'city': 'Abuja',
                    'address': '123 Main Street',
                    'full_name': 'John Doe',
                    'phone': '08000000000'
                },
                response_only=True,
            )
        ]
    ),

    create=extend_schema(
        description="Create a new order for the authenticated user.",
        examples=[
            OpenApiExample(
                'Order creation example',
                summary='Example order',
                description='Example request for creating an order.',
                value={
                    'full_name': 'John Doe',
                    'phone': '08000000000',
                    'address': '123 Main Street',
                    'city': 'Abuja',
                    'state': 'FCT',
                    'items': [
                        {
                            'product': 1,
                            'quantity': 2
                        }
                    ]
                },
                request_only=True,
            )
        ]
    ),

    update=extend_schema(
        description="Update an order belonging to the authenticated user.",
        responses={
        200: OrderSerializer,
        400: OpenApiResponse(
            description="Invalid order data."
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(
            description="Order not found."
        ),
    },
    ),

    partial_update=extend_schema(
        description="Partially update an order belonging to the authenticated user.",
        responses={
        200: OrderSerializer,
        400: OpenApiResponse(
            description="Invalid order data."
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(
            description="Order not found."
        ),
    },
    ),

    destroy=extend_schema(
        description="Delete an order belonging to the authenticated user.",
         responses={
        204: OpenApiResponse(
            description="Order successfully deleted."
        ),
        401: OpenApiResponse(
            description="Authentication credentials were not provided."
        ),
        404: OpenApiResponse(
            description="Order not found."
        ),
    },
    ),
)
class OrderViewSet(viewsets.ModelViewSet):

    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(
            user=self.request.user
        ).prefetch_related(
            'items__product'
        )    



    
    
    


