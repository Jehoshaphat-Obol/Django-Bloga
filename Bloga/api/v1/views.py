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
        "group": reverse('v1:group-list', request=request)
    })