from django.urls import path
from . import views

urlpatterns = [
    path("user/", views.UserListView.as_view(), name="user-list"),
    path("user/<str:username>/", views.UserDetailView.as_view(), name="user-detail"),
    path('group/', views.GroupListView.as_view(), name="group-list"),
    path('group/<str:name>', views.GroupDetailView.as_view(), name='group-detail'),
    path('profiles/', views.ProfileListView.as_view(), name='profile-list'),
    path('profiles/<int:pk>/', views.ProfileDetailView.as_view(), name='profile-detail'),
]