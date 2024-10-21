from django.urls import include, path
from rest_framework import routers
from .authentication import views as auth_views
from .blog import views as blog_views
from . import views
from knox import views as knox_views

urlpatterns = [
    path("",views.root, name="root"),
    path('auth/', include('rest_framework.urls', namespace='rest_framework')),    
    path("api/login/", auth_views.LoginAPI.as_view(), name='login'),
    path('api/logout/', knox_views.LogoutView.as_view(), name='logout'),
    path('api/logoutall/', knox_views.LogoutAllView.as_view(), name='logoutall'),
    path("user/", auth_views.UserListView.as_view(), name="user-list"),
    path("user/<str:username>/", auth_views.UserDetailView.as_view(), name="user-detail"),
    path('group/', auth_views.GroupListView.as_view(), name="group-list"),
    path('group/<str:name>', auth_views.GroupDetailView.as_view(), name='group-detail'),
    path('post/', blog_views.PostsListView.as_view(), name='posts-list'),
    path('post/<slug:link>/', blog_views.PostsDetailView.as_view(), name='posts-detail'),
    path("comment/", blog_views.CommentsListView.as_view(), name='comments-list'),
    path("comment/<int:pk>/", blog_views.CommentsDetailView.as_view(), name='comments-detail'),
    path("post-reaction/", blog_views.PostReactionsListView.as_view(), name="postreactions-list"),
    path("post-reaction/<int:pk>/", blog_views.PostReactionsDetailView.as_view(), name="postreactions-detail"),
    path("comment-reaction/", blog_views.CommentReactionsListView.as_view(), name="commentreactions-list"),
    path("comment-reaction/<int:pk>/", blog_views.CommentReactionsDetailView.as_view(), name="commentreactions-detail"),
    path("saved-post/", blog_views.SavedPostListView.as_view(), name="savedpost-list"),
    path("saved-post/<int:pk>/", blog_views.SavedPostDetailView.as_view(), name="savedpost-detail"),
    path('profiles/', auth_views.ProfileListView.as_view(), name='profile-list'),
    path('profiles/<int:pk>/', auth_views.ProfileDetailView.as_view(), name='profile-detail'),
]

