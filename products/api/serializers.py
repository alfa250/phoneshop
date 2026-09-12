from rest_framework import serializers
from products.models import Product, Order, OrderItem, User
from products.services import create_order



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'is_staff',
            'is_superuser'
        )


class ProductSerializer(serializers.ModelSerializer):
    current_price = serializers.ReadOnlyField()

    class Meta:
        model = Product
        fields = (
            'id',
            'name',
            'description',
            'price',
            'sale_price',
            'is_sale',
            'stock',
            'category',
            'current_price'
    

        )

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source = 'product.name', read_only = True)
    product_price = serializers.DecimalField(source = 'price', read_only = True,
                                        max_digits = 10, decimal_places = 2)

    class Meta:
        model = OrderItem
        fields = (
            'product',
            'product_name',
            'product_price',
            'quantity', 
            'subtotal'
        )
        read_only_fields = (
            'product_name',
            'product_price',
            'subtotal'
        )




class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only = True)
    items = OrderItemSerializer(many = True)
    total_price = serializers.SerializerMethodField()
    def get_total_price(self, obj):
        return sum(item.subtotal for item in obj.items.all())
        
    def create(self, validated_data):
        items = validated_data.pop('items')
        request = self.context['request']
        try:
                
            order = create_order(
                user=request.user,
                items=items,
                full_name=validated_data.get('full_name'),
                phone=validated_data.get('phone'),
                address=validated_data.get('address'),
                city=validated_data.get('city'),
                state=validated_data.get('state')
            )
        except ValueError as e:
            raise serializers.ValidationError({'items': str(e)})
        return order
    
    class Meta:
        model = Order
        fields = (
            'user',
            'order_id',
            'status',
            'items',
            'total_price',
            'state',
            'city',
            'address',
            'full_name',
            'phone',

        )
        read_only_fields = (
            'user',
            'order_id',
            'total_price'
        )
    

class ProductInfoSerializer(serializers.Serializer):
    # This serializer is used to display product information in the order details.
    product = ProductSerializer(many = True)
    count = serializers.IntegerField()
    max_price = serializers.FloatField()

    
    
    