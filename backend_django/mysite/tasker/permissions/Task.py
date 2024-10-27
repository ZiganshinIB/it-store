from rest_framework import permissions

class IsNew(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.status == 'new'


class CanChange(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.status in ['new', 'prg', 'aprv']