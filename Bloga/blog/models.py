from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify
import string, random
from taggit.managers import TaggableManager

# Create your models here.
class PublishedManager(models.Manager):
    """
    A manager that filters out draft posts and returns only published posts
    """
    def get_queryset(self):
        return (
            super().get_queryset().filter(status=Posts.Status.PUBLISHED)
        )

def random_string_generator(size=6, chars=string.ascii_lowercase + string.digits):
    """Generate a random string of a given size"""
    return "".join(random.choice(chars) for _ in range(size))

class Posts(models.Model):
    """
    Posts Models
    """
    
    class Status(models.TextChoices):
        DRAFT = 'DF', 'Draft'
        PUBLISHED = 'PB', 'Published'
        
    title = models.CharField(max_length=250, blank=False, null=False, default='New Blog')
    content = models.TextField()
    link = models.SlugField(unique=True, max_length=250)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT
    )
    publish = models.DateTimeField(default=None, blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    tags = TaggableManager()
    
    class Meta:
        ordering = ['-publish']
        indexes = [
            models.Index(fields=['-publish'])
        ]
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
    
    # Add Custom Managers
    objects = models.Manager()
    published = PublishedManager()
    
    def __str__(self):
        return self.title
    
    def save(self, update=False, *args, **kwargs):
        """
        Extend the function used to save posts to make sure that links are always unique
        """
        
        if update:
            super().save(*args, **kwargs)
            return 
        
        if not self.link:
            # generate initial slug based on title
            self.link = slugify(self.title)
            
        # Check link uniqueness
        original_link = self.link
        queryset = Posts.objects.filter(link=self.link)
        counter = 1
        
        while queryset.exists():
            # Append random characters if link is not unique
            random_str = random_string_generator(size= 4 + counter)
            self.link = f"{original_link}-{random_str}"
            queryset = Posts.objects.filter(link=self.link)
            counter += 1
        
        # set publish to now when ever the status is changed from draft to published
        if not Posts.published.filter(link=self.link).exists() and self.status == "PB":
            self.publish = timezone.now()
        else:
            self.publish = None
        # save the model    
        super().save(*args, **kwargs)
        
class Comments(models.Model):
    post = models.ForeignKey(Posts, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(blank=False)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        
    def save(self, *args, **kwargs):
        # avoid commenting on draft posts
        if self.post.status == 'DF':
            return
        
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"comment: {self.content[:10]}... on {self.post.title[:10]}..."
        
        
class PostReactions(models.Model):
    class Reactions(models.TextChoices):
        LIKE = 'LK', 'LIKE'
        
    post = models.ForeignKey(Posts, related_name='reactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='reactions', on_delete=models.CASCADE)
    reaction = models.CharField(
        max_length=2,
        choices=Reactions,
        default=Reactions.LIKE
    )  
    
    class Meta:
        unique_together = ['post', 'user']
        verbose_name = 'Post Reaction'
        
    def save(self, *args, **kwargs):
        if self.post.status == "DF":
            return
        
        if PostReactions.objects.filter(user=self.user, post=self.post).exists():
            return
        
        super().save(*args, **kwargs)
          
class CommentReactions(models.Model):
    class Reactions(models.TextChoices):
        LIKE = 'LK', 'LIKE'
        
    comment = models.ForeignKey(Comments, related_name='reactions', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comment_reactions', on_delete=models.CASCADE)
    reaction = models.CharField(
        max_length=2,
        choices=Reactions,
        default=Reactions.LIKE
    )
    
    class Meta:
        unique_together = ['comment', 'user']
        verbose_name = 'Comments Reaction'
        
    def save(self, *args, **kwargs):
        if self.comment.post.status == "DF":
            return
        
        if CommentReactions.objects.filter(user=self.user, comment=self.comment).exists():
            return
        super().save(*args, **kwargs)
        
class SavedPost(models.Model):
    user = models.ForeignKey(User, related_name='saved', on_delete=models.CASCADE)
    post = models.ForeignKey(Posts, related_name='savers', on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'post']
        
    def save(self, *args,**kwargs):
        if self.post.status == "DF":
            return
        
        if SavedPost.objects.filter(user=self.user, post=self.post).exists():
            return
        
        super().save(*args, **kwargs)