from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("posts/", views.posts_list, name="post_list"),
    path("posts/<slug:link>/",views.post_detail, name="post"),
    path("posts/<slug:link>/edit/",views.post_edit, name="post_edit"),
    path("posts/<slug:link>/delete/",views.post_delete, name="post_delete"),
    path("posts/<slug:link>/like/",views.post_like, name="post_like"),
    path("posts/<slug:link>/comment/",views.post_comment, name="post_comment"),
    path("posts/<slug:link>/save/",views.post_save, name="post_save"),
    path("posts/comment/<str:comment_id>/like/",views.comment_like, name="comment_like"),
    path("write/", views.write, name="write"),
    path("tags/", views.tags_list, name="tags_list"),
    path("tags/<str:name>/", views.tag, name="tag"),
    path("users/", views.user_list, name="user_list"),
    path("users/<str:username>/", views.profile, name="profile"),
    path("users/<str:username>/saved/", views.user_saved, name="user_saved"),
    path("users/<str:username>/favorites/", views.user_favorites, name="user_favorites"),
    path("users/<str:username>/following/", views.user_following, name="user_following"),
    path("users/<str:username>/followers/", views.user_followers, name="user_followers"),
    path("users/<str:username>/edit/", views.user_edit, name="user_edit"),
    path("users/<str:username>/follow/", views.user_follow, name="user_follow"),
    path("users/<str:username>/unfollow/", views.user_unfollow, name="user_unfollow"),
]