from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

@api_view(['GET'])
def root(request):
    """
    API V1 Root
    """
    return Response({
        "user": reverse('v1:user-list', request=request),
        "profile": reverse("v1:profile-list", request=request),
        "group": reverse('v1:group-list', request=request),
        "post": reverse("v1:posts-list", request=request),
        "comment": reverse("v1:comments-list", request=request),
        "post-reaction": reverse("v1:postreactions-list", request=request),
        "comment-reaction": reverse("v1:commentreactions-list", request=request),
        "saved-post": reverse("v1:savedpost-list", request=request),
    })