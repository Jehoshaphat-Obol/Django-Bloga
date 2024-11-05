from django.urls import path, include
from . import views

urlpatterns = [
    path('post/', views.PostsListView.as_view(), name='posts-list'),
    path('post/<slug:link>/', views.PostsDetailView.as_view(), name='posts-detail'),
    path("comment/", views.CommentsListView.as_view(), name='comments-list'),
    path("comment/<int:pk>/", views.CommentsDetailView.as_view(), name='comments-detail'),
    path("post-reaction/", views.PostReactionsListView.as_view(), name="postreactions-list"),
    path("post-reaction/<int:pk>/", views.PostReactionsDetailView.as_view(), name="postreactions-detail"),
    path("comment-reaction/", views.CommentReactionsListView.as_view(), name="commentreactions-list"),
    path("comment-reaction/<int:pk>/", views.CommentReactionsDetailView.as_view(), name="commentreactions-detail"),
    path("saved-post/", views.SavedPostListView.as_view(), name="savedpost-list"),
    path("saved-post/<int:pk>/", views.SavedPostDetailView.as_view(), name="savedpost-detail"),
]