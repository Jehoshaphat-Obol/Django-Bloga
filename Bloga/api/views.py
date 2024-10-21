from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

@api_view(['GET'])
def root(request):
    """
    API V1 Root
    """
    return Response({
        "login": reverse("login", request=request),
        "logout": reverse("logout", request=request),
        "logoutall": reverse("logoutall", request=request),
        "user": reverse('user-list', request=request),
        "profile": reverse("profile-list", request=request),
        "group": reverse('group-list', request=request),
        "post": reverse("posts-list", request=request),
        "comment": reverse("comments-list", request=request),
        "post-reaction": reverse("postreactions-list", request=request),
        "comment-reaction": reverse("commentreactions-list", request=request),
        "saved-post": reverse("savedpost-list", request=request),
    })