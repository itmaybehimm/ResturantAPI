from django.contrib.auth.models import User, Group

from rest_framework.decorators import api_view, permission_classes
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from .custompermissions import IsManager, IsCustomer, IsDeliveryCrew
from .serializer import UserSerializer, MenuItemSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from .models import MenuItem, Cart, Order, OrderItem
# Create your views here.


# def isCustomer(user):
#     if (user.groups.filter(name='Manager').exists() or user.groups.filter(name='Delivery Crew').exists()):
#         return False
#     else:
#         return True


class MenuViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsManager]
        return [permission() for permission in permission_classes]


@api_view(['GET', 'POST'])
@permission_classes([IsManager])
def manage_manager(request):
    if not Group.objects.filter(name='Manager').exists():
        Group.objects.create(name='Manager').save()

    if request.method == 'GET':
        users = User.objects.filter(
            groups__name='Manager') | User.objects.filter(is_superuser=True)
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            group = Group.objects.get(name='Manager')
            if user.groups.filter(name='Manager').exists():
                return Response({"message": f"{username} is already a manager"}, status=status.HTTP_200_OK)
            user.groups.add(group)
            return Response({"message": f"{username} added to managers"}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsManager])
def delete_manager(request, id):
    try:
        user = User.objects.get(pk=id)
        group = Group.objects.get(name='Manager')
        if not user.groups.filter(name='Manager').exists():
            return Response({"message": f"{user.username} is not a manager"}, status=status.HTTP_200_OK)
        user.groups.remove(group)
        return Response({"message": f"{user.username} removed from managers"}, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
@permission_classes([IsManager])
def manage_delivery_crew(request):
    if not Group.objects.filter(name='Delivery Crew').exists():
        Group.objects.create(name='Delivery Crew').save()

    if request.method == 'GET':
        users = User.objects.filter(
            groups__name='Delivery Crew')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            user = User.objects.get(username=username)
            group = Group.objects.get(name='Delivery Crew')
            if user.groups.filter(name='Delivery Crew').exists():
                return Response({"message": f"{username} is already a delivery crew"}, status=status.HTTP_200_OK)
            user.groups.add(group)
            return Response({"message": f"{username} added to delivery crew"}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsManager])
def delete_delivery_crew(request, id):
    try:
        user = User.objects.get(pk=id)
        group = Group.objects.get(name='Delivery Crew')
        if not user.groups.filter(name='Delivery Crew').exists():
            return Response({"message": f"{user.username} is not a deliver crew"}, status=status.HTTP_200_OK)
        user.groups.remove(group)
        return Response({"message": f"{user.username} removed from deliver crew"}, status=status.HTTP_201_CREATED)
    except User.DoesNotExist:
        return Response({"message": "User not found"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsCustomer])
def cart_view(request):
    user = request.user
    if (request.method == 'GET'):
        cart_items = Cart.objects.filter(user=user)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    if (request.method == 'POST'):
        try:
            data = {}
            item = MenuItem.objects.get(pk=request.POST.get('menuitem'))
            data['user'] = user.id
            data['menuitem_id'] = item.id
            data['unit_price'] = item.price
            data['quantity'] = request.POST.get('quantity')
            data['price'] = float(item.price) * float(data['quantity'])
            if (Cart.objects.filter(user=user.id).filter(menuitem=item.id).exists()):
                return Response({'message': 'Already Exists'}, status=status.HTTP_200_OK)
            serializer = CartSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except MenuItem.DoesNotExist:
            return Response({'message': 'Item doesnt exist'}, status=status.HTTP_404_NOT_FOUND)
        except Exception:
            return Response({'message': 'Invalid Data'}, status=status.HTTP_400_BAD_REQUEST)

    if (request.method == 'DELETE'):
        cart_items = Cart.objects.filter(user=user)
        for item in cart_items:
            item.delete()
        return Response({'message': 'Cart Deleted'}, status=status.HTTP_200_OK)


@api_view(['GET', 'POST',])
@permission_classes([IsAuthenticated])
def order_view(request):
    user = request.user
    if (request.method == 'GET'):
        if (user.groups.filter(name='Manager').exists()):
            try:
                orders = Order.objects.all()
                order_serializer = OrderSerializer(orders, many=True)
                return Response(order_serializer.data, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({'message': "No Orders"}, status=status.HTTP_404_NOT_FOUND)
        elif (user.groups.filter(name='Delivery Crew').exists()):
            try:
                orders = Order.objects.filter(delivery_crew=user)
                order_serializer = OrderSerializer(orders, many=True)
                return Response(order_serializer.data, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({'message': "No Orders"}, status=status.HTTP_404_NOT_FOUND)
        else:
            try:
                orders = Order.objects.filter(user=user)
                order_serializer = OrderSerializer(orders, many=True)
                return Response(order_serializer.data, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({'message': "No Orders"}, status=status.HTTP_404_NOT_FOUND)

    if (request.method == 'POST'):
        if (user.groups.filter(name='Manager').exists()):
            return Response({'message': "Manager Cannot Process"}, status=status.HTTP_400_BAD_REQUEST)
        elif (user.groups.filter(name='Delivery Crew').exists()):
            return Response({'message': "Delivery Crew Cannot Process"}, status=status.HTTP_400_BAD_REQUEST)
        else:
            try:
                cart_items = Cart.objects.filter(user=user)
                if len(cart_items) == 0:
                    return Response({'message': 'Empty Cart'}, status=status.HTTP_400_BAD_REQUEST)

                total = 0
                data = {}
                order_data = {}
                order_data['user'] = user.id
                order_data['total'] = total
                order_serializer = OrderSerializer(data=order_data)
                order_serializer.is_valid(raise_exception=True)
                placed_order = order_serializer.save()

                for item in cart_items:
                    data['order_id'] = placed_order.id
                    data['menuitem_id'] = item.menuitem.id
                    data['quantity'] = item.quantity
                    data['unit_price'] = item.unit_price
                    total = total + float(item.unit_price)*float(item.quantity)
                    order_item_serializer = OrderItemSerializer(data=data)

                    order_item_serializer.is_valid(raise_exception=True)
                    order_item_serializer.save()
                    item.delete()

                placed_order.total = total
                placed_order.save()

                return Response(order_serializer.data, status=status.HTTP_201_CREATED)

            except Exception as e:
                return Response({'message': f"{e}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'PUT', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
def order_id_view(request, id):
    user = request.user
    if (request.method == 'GET'):
        if (user.groups.filter(name='Manager').exists()):
            return Response({'message': "Manager Cannot Process"}, status=status.HTTP_400_BAD_REQUEST)

        elif (user.groups.filter(name='Delivery Crew').exists()):
            return Response({'message': "Delivery Crew Cannot Process"}, status=status.HTTP_400_BAD_REQUEST)

        else:
            try:
                order = Order.objects.get(pk=id)
                if (order.user != user):
                    return Response({'message': "Not Authorized"}, status=status.HTTP_401_UNAUTHORIZED)
                order_serializer = OrderSerializer(order)
                return Response(order_serializer.data, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({'message': "Order doesn t exist"}, status=status.HTTP_404_NOT_FOUND)
        return Response({'message': "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)

    if (request.method == 'PATCH'):
        if (user.groups.filter(name='Delivery Crew').exists()):
            data = request.POST
            stat = data.get('status')
            try:
                order = Order.objects.get(pk=id)
                if (stat == '1'):
                    order.status = True
                elif (stat == '0'):
                    order.status = False
                else:
                    return Response({'message': "Bad Request"}, status=status.HTTP_400_BAD_REQUEST)
                order.save()
                return Response({'message': "Scucessfull"}, status=status.HTTP_200_OK)
            except Order.DoesNotExist:
                return Response({'message': "Order doesn t exist"}, status=status.HTTP_404_NOT_FOUND)

        if (user.groups.filter(name='Manager').exists()):
            try:
                order = Order.objects.get(pk=id)
                if (order.status != None):
                    return Response({'message': f"Already Assigned"}, status=status.HTTP_200_OK)
                crew = User.objects.get(username=request.POST.get('username'))
                if (not crew.groups.filter(name='Delivery Crew').exists()):
                    return Response({'message': "User is not crew member"}, status=status.HTTP_400_BAD_REQUEST)
                order.delivery_crew = crew
                order.status = False
                order.save()
                return Response({'message': "Scucessfull"}, status=status.HTTP_201_CREATED)

            except Order.DoesNotExist:
                return Response({'message': "Order doesn t exist"}, status=status.HTTP_404_NOT_FOUND)
            except User.DoesNotExist:
                return Response({'message': "Username doesn t exist"}, status=status.HTTP_404_NOT_FOUND)

        return Response({'message': "Not Authorized"}, status=status.HTTP_401_UNAUTHORIZED)

    if (request.method == 'DELETE'):
        if (user.groups.filter(name='Manager').exists()):
            order = Order.objects.get(pk=id)
            order.delete()
            return Response({'message': f"Deleted Order {id}"}, status=status.HTTP_200_OK)
        return Response({'message': "Not Authorized"}, status=status.HTTP_401_UNAUTHORIZED)
