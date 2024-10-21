from rest_framework import serializers
from blog.models import (
    Posts, Comments, PostReactions, CommentReactions,
    SavedPost
)
from taggit.serializers import TagListSerializerField, TaggitSerializer


class PostsSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    status = serializers.ChoiceField(choices=Posts.Status.choices)
    tags = TagListSerializerField(required=False)
    
    
    class Meta:
        model = Posts
        fields = ['url','title', 'content', 'status', 'tags', 'link', 'author', 'publish', 'created', 'updated']
        extra_kwargs = {
            "link":  {"read_only": True},
            "author": {"read_only": True},
            "url": {"view_name": "posts-detail", "lookup_field": "link"},
            "author": {"view_name": "user-detail", "lookup_field": "username", "read_only": True},
            "publish": {"read_only": True},
            "created": {"read_only": True},
            "updated": {"read_only": True},
        }

    def save(self, **kwargs):
        author = kwargs.get('author')
        update = kwargs.get('update', False)
        
        if update:
            post = self.instance
            post.title = self.validated_data.get('title', post.title)
            post.content = self.validated_data.get('content', post.content)
            post.status = self.validated_data.get('status', post.status)
        else:
            post = Posts(
                title=self.validated_data['title'],
                content=self.validated_data['content'],
                status=self.validated_data['status'],
                author=author
            )

        # Save the post object
        post.save(update=update)

        post.tags.set(self.validated_data.get('tags', []))
        post.save(update=True)
        self.instance = post
        
        self.instance
        
        
class CommentsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Comments
        fields = ['url', 'post', 'user', 'content']
        extra_kwargs = {
            "url": {"view_name": "comments-detail"},
            "post": {"view_name": "posts-detail", "lookup_field": "link"},
            "user": {"view_name": "user-detail", "lookup_field": "username", "read_only": True},
        }
        

class PostReactionsSerializer(serializers.HyperlinkedModelSerializer):
    reaction = serializers.ChoiceField(choices=PostReactions.Reactions.choices)
    class Meta:
        model = PostReactions
        fields = ['url','post','user', 'reaction']
        extra_kwargs = {
            "url": {"view_name": "postreactions-detail"},
            "post": {"view_name": "posts-detail", "lookup_field": "link"},
            "user": {"view_name": "user-detail", "lookup_field": "username", "read_only": True},
        }        


class CommentReactionsSerializer(serializers.HyperlinkedModelSerializer):
    reaction = serializers.ChoiceField(choices=CommentReactions.Reactions.choices)
    class Meta:
        model = CommentReactions
        fields = ['url','comment','user', 'reaction']
        extra_kwargs = {
            "url": {"view_name": "commentreactions-detail"},
            "comment": {"view_name": "comments-detail", "lookup_field": "pk"},
            "user": {"view_name": "user-detail", "lookup_field": "username", "read_only": True},
        }
        
        
class SavedPostSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = SavedPost
        fields = ['url', 'user', 'post']
        extra_kwargs = {
            "url": {"view_name": "savedpost-detail", "lookup_field": "pk"},
            "user": {"view_name": "user-detail", "lookup_field": "username", "read_only": True},
            "post": {"view_name": "posts-detail", "lookup_field": "link"},   
        }
        
