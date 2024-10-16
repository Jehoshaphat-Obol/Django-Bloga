from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

@api_view(['GET'])
def root(request):
    """
    API V2 Root
    """
    return Response({
        "user": reverse('v2:user-list', request=request),
    })