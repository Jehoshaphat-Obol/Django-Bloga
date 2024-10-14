from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages

from .models import Posts

def is_post_owner(func):
    def wrapper(request, *args, **kwargs):
        link = kwargs.get('link')
        post = get_object_or_404(
            Posts,
            link=link
        )
        
        if post.author != request.user:
            messages.error(request, "Action Forbiden")
            return redirect('blog:post', link=link)
        
        return func(request, *args, **kwargs)
    
    return wrapper