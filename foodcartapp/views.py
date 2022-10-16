import json
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.serializers import Serializer, ModelSerializer, ValidationError
from rest_framework.serializers import CharField

from .models import Product, Order, OrderProduct


class OrderProductSerializer(ModelSerializer):
    class Meta:
        model = OrderProduct
        fields = ['product', 'quantity']


class OrderSerializer(ModelSerializer):
    products = OrderProductSerializer(many=True)

    class Meta:
        model = Order
        fields = ['firstname', 'lastname', 'phonenumber', 'address', 'products']


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    content = request.data
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    products = request.data.get('products', [])
    if not isinstance(products, list):
        raise ValidationError('Expects products field be a list')
    if not products:
        raise ValidationError('Products field must be not null')

    for fields in products:
        serializer = OrderProductSerializer(data=fields)
        serializer.is_valid(raise_exception=True)

    order = Order.objects.create(
        firstname=content['firstname'],
        lastname=content['lastname'],
        phonenumber=content['phonenumber'],
        address=content['address']
    )
    for product in content['products']:
        OrderProduct.objects.create(
            product=Product.objects.get(id=product['product']),
            order=Order.objects.get(id=order.id),
            quantity=product['quantity']
        )
    return Response({})
