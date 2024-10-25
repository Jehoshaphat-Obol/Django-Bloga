from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveDestroyAPIView
from rest_framework import permissions
from blog.models import (
    Posts, Comments, PostReactions, CommentReactions,
    SavedPost
)
from .serializers import (
    PostsSerializer, CommentsSerializer, PostReactionsSerializer,
    CommentReactionsSerializer, SavedPostSerializer
)
from django.db.models import Q
from .permissions import(
    IsPostOwernerOrReadOnly, IsCommentOwernerOrReadOnly, IsPostReactionOwernerOrReadOnly,
    IsCommentReactionOwernerOrReadOnly, IsSavedPostOwerner
)


class PostsListView(ListCreateAPIView):
    """
    API v1 endpoint for Posts
    """
    queryset = Posts.objects.all().order_by('-publish')
    serializer_class = PostsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    lookup_field = 'link'
    

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
        
    # list should contain published post and owner's draftpost
    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            self.queryset = Posts.published.all().order_by('-publish')
        else:
             self.queryset = Posts.objects.filter(Q(status="PB") | Q(status='DF', author=user)).all().order_by('-publish')
        return self.queryset
       
    
class PostsDetailView(RetrieveUpdateDestroyAPIView):
    """
    API v1 endpoint for Posts instances
    """
    queryset = Posts.objects.all()
    serializer_class = PostsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsPostOwernerOrReadOnly]
    lookup_field = 'link'
    
    def perform_update(self, serializer):
        serializer.save(instance=self.get_object(), update=True)
        
        
class CommentsListView(ListCreateAPIView):
    """
    API v1 endpoint for Comments
    Note that can on create if post is published
    """
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]


    def perform_create(self, serializer):
        comment = Comments(user=self.request.user)
        serializer.instance = comment
        return super().perform_create(serializer)
    
    
class CommentsDetailView(RetrieveUpdateDestroyAPIView):
    """
    API v1 endpoint for Comments instances
    Note that can on update and destroy if post is published
    """
    queryset = Comments.objects.all()
    serializer_class = CommentsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentOwernerOrReadOnly]


class PostReactionsListView(ListCreateAPIView):
    """
    API v1 endpoint for post reactions
    Note: It only creates if the post is published
    """
    queryset = PostReactions.objects.all()
    serializer_class = PostReactionsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    
    # user set depending on who is authenticated
    def perform_create(self, serializer):
        user = self.request.user
        reaction = PostReactions(user=user)
        serializer.instance = reaction
        return super().perform_create(serializer)    


class PostReactionsDetailView(RetrieveDestroyAPIView):
    """
    API v1 endpoint for post reactions instances
    Note: It only creates if the post is published
    """
    queryset = PostReactions.objects.all()
    serializer_class = PostReactionsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsPostReactionOwernerOrReadOnly]


class CommentReactionsListView(ListCreateAPIView):
    """
    API v1 endpoint for comment reactions
    Note: It only creates if the comment for a published post
    """
    queryset = CommentReactions.objects.all()
    serializer_class = CommentReactionsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly,]
    
    # user set depending on who is authenticated
    def perform_create(self, serializer):
        user = self.request.user
        reaction = CommentReactions(user=user)
        serializer.instance = reaction
        return super().perform_create(serializer)    


class CommentReactionsDetailView(RetrieveDestroyAPIView):
    """
    API v1 endpoint for post reactions instances
    Note: It only creates if the post is published
    """
    queryset = CommentReactions.objects.all()
    serializer_class = CommentReactionsSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsCommentReactionOwernerOrReadOnly]


class SavedPostListView(ListCreateAPIView):
    """
    API v1 endpoint for saved posts
    """
    queryset = SavedPost.objects.all()
    serializer_class = SavedPostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # only how saved post that belong to the user
    def get_queryset(self):
        user=self.request.user
        self.queryset = SavedPost.objects.filter(user=user).all()
        return super().get_queryset()
    
    # default owner of a saved post is the authenticated user
    def perform_create(self, serializer):
        saved = SavedPost(user=self.request.user)
        serializer.instance = saved
        return super().perform_create(serializer)
    
    

class SavedPostDetailView(RetrieveDestroyAPIView):
    """
    API v1 endpoint for the saved post instances
    """
    queryset = SavedPost.objects.all()
    serializer_class = SavedPostSerializer
    permission_classes = [permissions.IsAuthenticated, IsSavedPostOwerner]