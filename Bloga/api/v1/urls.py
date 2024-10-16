from django.urls import include, path
from rest_framework import routers
from .authentication import views as auth_views
from .blog import views as blog_views
from . import views

app_name = "v1"
urlpatterns = [
    path("",views.root),
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
]

