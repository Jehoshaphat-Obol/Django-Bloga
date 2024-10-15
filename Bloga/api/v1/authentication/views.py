from rest_framework import permissions, viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.models import User, Group

from .serializers import UserSerializer, GroupSerializer
from .permissions import (
    IsAccountOwnerOrReadOnly,
    IsSuperUser,
)

class UserListView(ListCreateAPIView):
    """
    API V1 endpoint for users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]    
    
class UserDetailView(RetrieveUpdateDestroyAPIView):
    """
    API V1 endpoint for user instances
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAccountOwnerOrReadOnly]
    lookup_field = 'username'
    

    
class GroupListView(ListCreateAPIView):
    """
    API v1 endpoint for groups
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    
class GroupDetailView(RetrieveUpdateDestroyAPIView):
    """
    API v1 endpoint for group instances
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated, IsSuperUser]
    lookup_field = 'name'