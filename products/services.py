from django.db import transaction
from products.models import Product, Order, OrderItem


@transaction.atomic
def create_order(
    *,
    user,
    items,
    full_name,
    phone,
    address,
    city,
    state
):
    total = 0
    order_items = []
#item['product'] should give you the product instance, not the product_id. So you should use item['product'].id to get the product_id.
    # 1. Validate products and stock
    for item in items:
        product = item['product']
        quantity = item['quantity']

        try:
            product = Product.objects.get(pk=product.id)
        except Product.DoesNotExist:
            raise ValueError(
                f'Product {product_id} does not exist.'
            )

        if product.stock < quantity:
            raise ValueError(
                f'Not enough stock for {product.name}. '
                f'Available: {product.stock}, '
                f'requested: {quantity}.'
            )

        # 2. Capture current price
        price = product.current_price

        # 3. Calculate subtotal
        subtotal = price * quantity

        # 4. Add to total
        total += subtotal

        # 5. Store information temporarily
        order_items.append({
            'product': product,
            'quantity': quantity,
            'price': price,
        })

    # 6. Create the Order
    order = Order.objects.create(
        user=user,
        full_name=full_name,
        phone=phone,
        address=address,
        city=city,
        state=state,
        total=total,
    )

    # 7. Create OrderItems and reduce stock
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

    return order