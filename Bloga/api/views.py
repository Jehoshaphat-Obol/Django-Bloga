from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.reverse import reverse

@api_view(['GET'])
def root(request):
    """
    API Root
    """
    return Response({
        "Browsable Authentication": reverse("rest_framework:login", request=request),
        "Version 1": reverse("v1:root", request=request),
        "Version 2": reverse("v2:root", request=request),
    })