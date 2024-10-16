from rest_framework.permissions import BasePermission

class IsAccountOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET','HEAD', 'OPTIONS']:
            return True

        return request.user == obj
    
class IsProfileOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in ['GET','HEAD', 'OPTIONS']:
            return True

        return request.user == obj.user

class IsSuperUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser
    
    def has_permission(self, request, view):
        return request.user.is_superuser