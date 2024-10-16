from django.urls import include, path
from api.v2.authentication import views as auth_views
from . import views

app_name = "v2"
urlpatterns = [
    path("",views.root),
    path("user/", auth_views.UserListView.as_view(), name="user-list"),
    path("user/<str:username>/", auth_views.UserDetailView.as_view(), name="user-detail"),
]