from pprint import pprint
from django.db import IntegrityError
from django.db.models import Q, Sum, F
from rest_framework.authtoken.models import Token
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import render
import requests
import yaml
import json
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from yaml import load, Loader
from rest_framework.views import APIView
from .models import User, Shop, Category, Product, ProductInfo, Parameter, ProductParameter, Order, OrderItem, Contact
from .serializers import UserSerializer, ProductSerializer, ProductInfoSerializer, OrderSerializer, OrderItemSerializer


class ShopUpdate(APIView):
    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'message': 'authentication is required'}, status=403)
        if request.user.type != 'shop':
            return JsonResponse({'status': False, 'message': 'feature is not available for customers'}, status=403)
        update_file = request.data.get('update_file')
        if update_file:
            data = load(update_file.file, Loader=Loader)
            pprint(data)
            if data:
                if {'shop', 'categories', 'goods'}.issubset(data):
                    shop, created = Shop.objects.get_or_create(name=data['shop'])
                    for category in data['categories']:
                        if {'id', 'name'}.issubset(category):
                            category, created = Category.objects.get_or_create(id=category['id'], name=category['name'])
                            category.shops.add(shop.id)
                            category.save()
                    ProductInfo.objects.filter(shop_id=shop.id).delete()
                    for good in data['goods']:
                        if {'id', 'category', 'model', 'name', 'quantity', 'price', 'price_rrc', 'parameters'}\
                                .issubset(good):
                            product, created = Product.objects.get_or_create(
                                name=good['name'],
                                category_id=good['category']
                            )
                            product_info = ProductInfo.objects.create(
                                item_id=good['id'],
                                model=good['model'],
                                name=good['name'],
                                quantity=good['quantity'],
                                price=good['price'],
                                price_rrc=good['price_rrc'],
                                product_id=product.id,
                                shop_id=shop.id,
                            )
                            for name, value in good['parameters'].items():
                                parameter, created = Parameter.objects.get_or_create(name=name)
                                ProductParameter.objects.create(
                                    parameter_id=parameter.id,
                                    product_info_id=product_info.id,
                                    value=value,
                                )
                    return JsonResponse({'status': True, 'message': 'data loaded successfully'})
                return JsonResponse({'status': False, 'message': 'insufficient arguments'})
        return JsonResponse({'status': False, 'message': 'update file is required'})


class SignUp(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        if {'first_name', 'middle_name', 'last_name', 'username', 'email', 'password', 'company', 'position'}\
                .issubset(data):
            try:
                validate_password(data['password'])
            except ValidationError as error:
                return JsonResponse({'status': False, 'message': str(error)})
            else:
                user_serializer = UserSerializer(data=data)
                print(user_serializer)
                if user_serializer.is_valid():
                    user = user_serializer.save()
                    user.set_password(data['password'])
                    user.save()
                    # send confirmation email???
                    return JsonResponse({'status': True, 'message': 'user registered successfully'})
                else:
                    return JsonResponse({'status': False, 'message': user_serializer.errors})
        return JsonResponse({'status': False, 'message': 'insufficient arguments'})


class LogIn(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        if {'username', 'password'}.issubset(data):
            user = authenticate(request, username=data['username'], password=data['password'])
            if user is not None:
                token, created = Token.objects.get_or_create(user=user)
                return JsonResponse({'status': True, 'message': 'login successful', 'token': token.key})
            return JsonResponse({'status': False, 'message': 'login failed'})
        else:
            return JsonResponse({'status': False, 'message': 'insufficient arguments'})


class ProductList(ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ProductInfoView(APIView):
    def get(self, request, *args, **kwargs):
        shop_id = request.GET.get('shop_id')
        shop = Shop.objects.filter(id=shop_id).first()
        if shop:
            category_id = request.GET.get('category_id')
            category = Category.objects.filter(id=category_id).first()
            if category:
                queryset = ProductInfo.objects.filter(shop_id=shop.id, product__category_id=category.id)\
                    .select_related('shop', 'product__category').prefetch_related('product_parameters__parameter')\
                    .distinct()
                serializer = ProductInfoSerializer(queryset, many=True)
                return Response(serializer.data)
            return JsonResponse({'status': False, 'message': 'category not found'})
        return JsonResponse({'status': False, 'message': 'shop not found'})


class BasketView(APIView):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'message': 'authentication is required'}, status=403)
        order = Order.objects.filter(user_id=request.user.id, status='basket').prefetch_related(
            'order_items__product_info__product__category', 'order_items__product_info__product_parameters__parameter')\
            .first()
        total_sum = 0
        order_items = order.order_items.all()
        for order_item in order_items:
            price = order_item.quantity * order_item.product_info.price
            total_sum += price
        order.total_sum = total_sum
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data)

    def post(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'message': 'authentication is required'}, status=403)
        order_items = request.data.get('order_items')
        if order_items:
            order_items_count = 0
            order, created = Order.objects.get_or_create(user_id=request.user.id, status='basket')
            for order_item in order_items:
                order_item.update({'order': order.id})
                order_serializer = OrderItemSerializer(data=order_item)
                if order_serializer.is_valid():
                    try:
                        order_serializer.save()
                    except IntegrityError as error:
                        return JsonResponse({'status': False, 'message': str(error)})
                    else:
                        order_items_count += 1
                else:
                    return JsonResponse({'status': False, 'message': order_serializer.errors})
            return JsonResponse({'status': True, 'message': f'{order_items_count} order item(s) added successfully'})
        return JsonResponse({'status': False, 'message': 'insufficient arguments'})

    def delete(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'message': 'authentication is required'}, status=403)
        delete_item_id = request.GET.get('delete_item_id')
        order = Order.objects.filter(user_id=request.user.id, status='basket').prefetch_related('order_items').first()
        order.order_items.filter(id=delete_item_id).delete()
        if len(order.order_items.all()) == 0:
            Order.objects.filter(user_id=request.user.id, id=order.id).delete()
        return JsonResponse({'status': True, 'message': 'order item deleted successfully'})

    def put(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'status': False, 'message': 'authentication is required'}, status=403)
        update_item_id = request.GET.get('update_item_id')
        data = request.data.get('update_data')
        if data:
            order = Order.objects.filter(user_id=request.user.id, status='basket').prefetch_related('order_items').first()
            for update_data in data:
                OrderItem.objects.filter(order_id=order.id, id=update_item_id).update(quantity=update_data['quantity'])
            return JsonResponse({'status': True, 'message': 'order item quantity updated'})
        return JsonResponse({'status': False, 'message': 'insufficient arguments'})


class OrderView(APIView):
    pass


def order_confirmation():
    pass


def thanks_for_order():
    pass


def orders_list():
    pass


def order_info():
    pass
