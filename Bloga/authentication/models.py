from django.db import models
from django.contrib.auth.models import User
import uuid, os

def secure_filestore(instance, filename):
    """Function to provide secure names for files uploaded"""
    ext = filename.split('.')[-1]
    new_name = f"{uuid.uuid4()}.{ext}"
    return os.path.join("uploads/dp/", new_name)


class Profile(models.Model):
    """A model to store the profile information of users
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True) 
    dp = models.ImageField(upload_to=secure_filestore, blank=True, null=True)
    follows = models.ManyToManyField(User, related_name='following', blank=True)
    followers = models.ManyToManyField(User, related_name='followers', blank=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        
        # user can not follow self and can not have self as a followere
        if self.follows.filter(id=self.user.id).exists():
            self.follows.remove(self.user)
            
        if self.followers.filter(id=self.user.id).exists():
            self.followers.remove(self.user)
        
