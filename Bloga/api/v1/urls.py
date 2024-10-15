from django.urls import include, path
from rest_framework import routers
from .authentication import views as auth_views
from .blog import views as bloga_views
from . import views

app_name = "v1"
urlpatterns = [
    path("",views.root),
    path("user/", auth_views.UserListView.as_view(), name="user-list"),
    path("user/<str:username>/", auth_views.UserDetailView.as_view(), name="user-detail"),
    path('group/', auth_views.GroupListView.as_view(), name="group-list"),
    path('group/<str:name>', auth_views.GroupDetailView.as_view(), name='group-detail'),
]

