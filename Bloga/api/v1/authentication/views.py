from rest_framework import permissions, viewsets
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView
from django.contrib.auth.models import User, Group
from authentication.models import Profile
from .serializers import ProfileSerializer

from .serializers import UserSerializer, GroupSerializer
from .permissions import (
    IsAccountOwnerOrReadOnly,
    IsSuperUser, IsProfileOwnerOrReadOnly
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
    
    
class ProfileListView(ListCreateAPIView):
    """
    API v1 endpoint for profiles
    """
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'pk'

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ProfileDetailView(RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsProfileOwnerOrReadOnly]
    lookup_field = 'pk'

    def perform_update(self, serializer):
        profile = self.get_object()

        # Only allow the owner to update the profile
        if profile.user != self.request.user:
            raise PermissionDenied("You do not have permission to update this profile.")
        
        # Call the serializer's update method
        serializer.save()