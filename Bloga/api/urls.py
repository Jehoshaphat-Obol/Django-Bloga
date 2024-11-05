from django.urls import include, path
from rest_framework import routers
from .authentication import views as auth_views
from .blog import views as blog_views
from . import views
from knox import views as knox_views

urlpatterns = [
    path("",views.root, name="root"),
    path("", include("api.authentication.urls")),
    path("", include("api.blog.urls")),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),    
    path("login/", auth_views.LoginAPI.as_view(), name='login'),
    path('logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
]

