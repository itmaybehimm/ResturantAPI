from rest_framework import serializers
from django.contrib.auth.models import User
from .models import MenuItem, Category, Cart, Order, OrderItem


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.StringRelatedField(many=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'is_superuser',
                  'groups', 'date_joined']


class CategroySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class MenuItemSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField(read_only=True)
    category_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = MenuItem
        fields = '__all__'


class CartSerializer(serializers.ModelSerializer):
    # unit_price = serializers.SerializerMethodField(
    #     method_name='get_unit_price')
    # price = serializers.SerializerMethodField(method_name='price_calculate')
    menuitem = MenuItemSerializer(read_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Cart
        fields = '__all__'

    # def price_calculate(self, instance: Cart):
    #     return instance.unit_price*instance.quantity

    # def get_unit_price(self, instance: Cart):
    #     return instance.menuitem.price


class OrderItemSerializer(serializers.ModelSerializer):
    order_id = serializers.IntegerField(write_only=True)
    menuitem_id = serializers.IntegerField(write_only=True)
    menuitem = serializers.StringRelatedField(read_only=True)
    order = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = OrderItem
        fields = '__all__'


class OrderSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField(
        method_name="get_items", read_only=True)

    class Meta:
        model = Order
        fields = '__all__'

    def get_items(self, instance):
        items = OrderItem.objects.filter(order=instance)
        items_serializer = OrderItemSerializer(items, many=True)

        return items_serializer.data
