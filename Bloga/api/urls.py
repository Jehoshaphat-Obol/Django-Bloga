from django.urls import include, path

urlpatterns = [
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('v1/', include('api.v1.urls', namespace='v1')),
    path('v2/', include('api.v2.urls')),
]