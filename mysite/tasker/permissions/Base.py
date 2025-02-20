from rest_framework import permissions

class IsAuthor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.author == request.user

class IsExecutor(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.executor == request.user

class IsGroup(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.groups.filter(name=obj.group).exists()

class AdvanceDjangoModelPermissions(permissions.DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }

class IsCheck(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.status == 'chk'