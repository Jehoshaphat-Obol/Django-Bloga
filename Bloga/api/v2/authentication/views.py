from api.v1.authentication import views
from .serializers import (UserSerializer)

class UserListView(views.UserListView):
    """
    API v2 endpoint for users
    """
    serializer_class = UserSerializer
    
    
class UserDetailView(views.UserDetailView):
    """
    API v2 endpoint for users
    """
    serializer_class = UserSerializer