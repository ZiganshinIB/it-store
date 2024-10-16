
from rest_framework import permissions

class ListRequestPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return True
        return False

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.has_perm('tasker.view_request'):
            return True
        return obj.author == request.user or obj.executor == request.user or obj.group in request.user.groups.all()

class DetailRequestPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or request.user.has_perm('tasker.view_request'):
            return True
        return obj.author == request.user or obj.executor == request.user or obj.group in request.user.groups.all()

class CanselRequestPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class AppointRequestPermission(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.has_perm('tasker.change_request') or request.user.is_superuser or obj.executor == request.user:
            return True
        return False