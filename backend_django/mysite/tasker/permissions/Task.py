from rest_framework import permissions

class IsNew(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.status == 'new'