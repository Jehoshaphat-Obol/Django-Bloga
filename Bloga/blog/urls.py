from django.urls import path
from . import views

app_name = "blog"

urlpatterns = [
    path("", views.home, name="home"),
    path("posts/", views.posts_list, name="post_list"),
    path("posts/<slug:link>/",views.post_detail, name="post"),
    path("tags/", views.tags_list, name="tags_list"),
    path("tags/<str:name>/", views.tag, name="tag"),
    path("write/", views.write, name="write"),
    
]