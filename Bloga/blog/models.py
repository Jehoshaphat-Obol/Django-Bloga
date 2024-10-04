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
    publish = models.DateTimeField(default=timezone.now)
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
    
    def save(self, *args, **kwargs):
        """
        Extend the function used to save posts to make sure that links are always unique
        """
        
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
        
        # save the model    
        super().save(*args, **kwargs)