from django.http import JsonResponse
from rest_framework import permissions
    
class IsCarOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.owner
    
class IsRentCarOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user == obj.car.owner
    