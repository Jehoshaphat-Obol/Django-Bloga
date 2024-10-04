from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from taggit.models import Tag

from .models import Posts
from .forms import PostsForm

# Create your views here.
@login_required
def home(request):
    user = request.user
    posts = Posts.published.all()
    
    context = {
        "user": user,
        "posts": posts,
    }
    return render(request, 'blog/home.html', context)

# Create your views here.
@login_required
def posts_list(request):
    user = request.user
    posts = Posts.published.all()
    
    context = {
        "user": user,
        "posts": posts,
    }
    return render(request, 'blog/posts.html', context)

@login_required
def post_detail(request, link):
    user=request.user
    post = get_object_or_404(
        Posts,
        link=link
    )
    
    context = {
        "user": user,
        "post": post,
    }
    
    return render(request, 'blog/post.html', context)

@login_required
def tags_list(request):
    user=request.user
    tags = Tag.objects.all()
    
    context = {
        "user": user,
        "tags": tags,
    }
    
    return render(request, 'blog/tags.html', context)

@login_required
def tag(request, name):
    user=request.user
    posts = Posts.published.filter(tags__name__in=[name])
    
    context = {
        "user": user,
        "posts": posts,
        "tag": name,
    }
    
    return render(request, 'blog/tag.html', context)


@login_required
def write(request):
    user = request.user
    form = PostsForm()
    
    if request.method == "POST":
        data = request.POST
        form = PostsForm(data)
        if form.is_valid():
            print(data)
            title = form.cleaned_data.get('title')
            tags = form.cleaned_data.get('tags')
            status = form.cleaned_data.get('status')
            content = form.cleaned_data.get('content')
            
            post = Posts(title=title, content=content,status=status, author=user)
            post.save()
            print(post.status)
            
            if tags:
                tags = tags.split(",")
                for tag in tags:
                    tag = tag.lower()
                    tag, created = Tag.objects.get_or_create(name=tag)
                    
                    post.tags.add(tag)
                    
            post.save()
            
            if status == 'PB':    
                messages.success(request, f"Posted - {title}")
            else:
                messages.success(request, f"Saved - {title}")
                
            return redirect('blog:home')
        
        else:
            messages.error(request, ", ".join(form.error_messages))
            
    context = {
        "user": user,
        "form": form,
    }
    
    return render(request, 'blog/write.html', context)