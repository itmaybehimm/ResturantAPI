from rest_framework.permissions import BasePermission


class IsManager(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.groups.filter(name='Manager').exists():
            return True
        else:
            return False


class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or request.user.groups.filter(name='Delivery Crew').exists():
            return True
        else:
            return False


class IsCustomer(BasePermission):
    def has_permission(self, request, view):
        if request.user.is_superuser or not request.user.groups.filter(name='Delivery Crew').exists() or not request.user.groups.filter(name='Manager').exists():
            return True
        else:
            return False
