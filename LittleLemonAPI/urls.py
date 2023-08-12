from django.urls import path, include
from . import views
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('menu-items', views.MenuViewSet)

urlpatterns = [
    path('groups/manager/users', views.manage_manager, name='manage-manager'),
    path('groups/manager/users/<int:id>',
         views.delete_manager, name='manage-manager'),
    path('groups/manager/delivery-crew',
         views.manage_delivery_crew, name='manage-manager'),
    path('groups/manager/delivery-crew/<int:id>',
         views.delete_delivery_crew, name='manage-manager'),
    path('', include(router.urls)),
    path('cart/menu-items', views.cart_view),
    path('orders', views.order_view),
    path('orders/<int:id>', views.order_id_view),
]
