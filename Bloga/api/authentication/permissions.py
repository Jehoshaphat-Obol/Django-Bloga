from rest_framework.permissions import BasePermission
from authentication.models import Profile

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
    

class HasProfileorCanCreate(BasePermission):
    def has_permission(self, request, view,):
        if request.method == 'POST':
            return  not Profile.objects.filter(user=request.user).exists()
    
        return True
    
class IsSuperUser(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_superuser
    
    def has_permission(self, request, view):
        return request.user.is_superuser