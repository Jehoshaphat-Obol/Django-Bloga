from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from taggit.models import Tag
from django.contrib.auth.models import User
from django.contrib.auth import update_session_auth_hash

from authentication.forms import ProfileForm
from authentication.models import Profile
from .models import Posts, Comments, PostReactions, CommentReactions, SavedPost
from .forms import PostsForm, CommentsForm
from .permissions import is_post_owner

def home(request):
    user = request.user
    posts = Posts.published.all()
    
    context = {
        "user": user if user.is_authenticated else None,
        "posts": posts,
    }
    return render(request, 'blog/home.html', context)


def posts_list(request):
    user = request.user
    posts = Posts.published.all()
    
    context = {
        "user": user if user.is_authenticated else None,
        "posts": posts,
        "page_title": "Explore Posts 🧭",
    }
    return render(request, 'blog/posts.html', context)


def post_detail(request, link):
    user=request.user
    
    if user.is_authenticated and Posts.objects.filter(author=user, link=link, status="DF").exists():
        post = get_object_or_404(
            Posts,
            link=link,
        )
    else:
        post = get_object_or_404(
            Posts,
            link=link,
            status = "PB"
        )
    
    form = CommentsForm()
    
    context = {
        "user": user if user.is_authenticated else None,
        "post": post,
        "form": form,
    }
    
    return render(request, 'blog/post.html', context)


@login_required
@is_post_owner
def post_edit(request, link):
    user = request.user
    post = get_object_or_404(
        Posts,
        link=link
    )
    
    tags = ",".join(post.tags.names())
    form = PostsForm(
        initial={
            'title': post.title,
            'content': post.content,
            'status': post.status,
            'tags': tags,
        }
    )
        
    if request.method == "POST":
        data = request.POST
        form = PostsForm(data)
        if form.is_valid():
            title = form.cleaned_data.get('title')
            tags = form.cleaned_data.get('tags')
            status = form.cleaned_data.get('status')
            content = form.cleaned_data.get('content')
            
            post.title = title
            post.status = status
            post.content = content
            post.tags.clear()
            post.save(update=True)
            
            if tags:
                tags = tags.split(",")
                for tag in tags:
                    tag = tag.lower()
                    tag, created = Tag.objects.get_or_create(name=tag)
                    
                    post.tags.add(tag)
                    
            post.save(update=True)
            
            if status == 'PB':    
                messages.success(request, f"Updated - {title}")
            else:
                messages.success(request, f"Saved - {title}")
                
            return redirect('blog:post', link=link)
        
        else:
            messages.error(request, form.errors.as_text())
            
    context = {
        "user": user,
        "form": form,
    }
    
    return render(request, 'blog/write.html', context)    


@login_required
@is_post_owner
def post_delete(request, link):
    user = request.user
    post = get_object_or_404(
        Posts,
        link=link
    )
    title = post.title
    post.delete()
    messages.success(request,f"Deleted - {title}")
    return redirect("blog:home")


@login_required
def post_comment(request, link):
    post = get_object_or_404(
        Posts,
        link=link,
        status='PB'
    )
    user = request.user
    
    if request.method == 'POST':
        comment = Comments(post=post, user=user)
        form = CommentsForm(request.POST, instance=comment)
        
        if form.is_valid():
            form.save()
            messages.success(request, "comment posted")
        messages.error(request, form.errors.as_text())
    return redirect('blog:post', link=link)


@login_required
def post_like(request, link):
    # if like exist delete else create
    post = get_object_or_404(
        Posts,
        link=link
    )
    user = request.user
    
    if PostReactions.objects.filter(post=post, user=user).exists():
        reaction = PostReactions.objects.get(post=post, user=user)
        reaction.delete()
    else:
        reaction = PostReactions(post=post, user=user)
        reaction.save()
    
    return redirect('blog:post', link=link)


@login_required
def post_save(request, link):
    user = request.user
    post = get_object_or_404(
        Posts,
        link=link
    )
    
    if SavedPost.objects.filter(user=user, post=post).exists():
        bookmark = SavedPost.objects.get(user=user, post=post)
        bookmark.delete()
    else:
        bookmark = SavedPost(user=user, post=post)
        bookmark.save()
    
    return redirect('blog:post', link=link)


@login_required
def comment_like(request, comment_id):
    # if like exist delete else create
    comment = get_object_or_404(
        Comments,
        id=comment_id
    )
    user = request.user
    
    if CommentReactions.objects.filter(comment=comment, user=user).exists():
        reaction = CommentReactions.objects.get(comment=comment, user=user)
        reaction.delete()
    else:
        reaction = CommentReactions(comment=comment, user=user)
        reaction.save()
    
    return redirect('blog:post', link=comment.post.link)


def tags_list(request):
    user=request.user
    tags = Tag.objects.all()
    
    context = {
        "user": user if user.is_authenticated else None,
        "tags": tags,
    }
    
    return render(request, 'blog/tags.html', context)


def tag(request, name):
    user=request.user
    posts = Posts.published.filter(tags__name__in=[name])
    
    context = {
        "user": user if user.is_authenticated else None,
        "posts": posts,
        "tag": name,
    }
    
    return render(request, 'blog/tag.html', context)


def user_list(request):
    users = User.objects.exclude(is_superuser=True).exclude(is_active=False)
    user = request.user
    tags = Tag.objects.all()
    
    context = {
        "users": users,
        "user": user if user.is_authenticated else None,
        "tags": tags,
    }
    
    return render(request, 'blog/users.html', context)



def user_following(request, username):
    user = get_object_or_404(
        User,
        username=username,
    )
    users = user.profile.follows.all()
    tags = Tag.objects.all()
    
    user = request.user
    context = {
        "users": users,
        "user": user if user.is_authenticated else None,
        "tags": tags,
    }
    
    return render(request, 'blog/users.html', context)



def user_followers(request, username):
    user = get_object_or_404(
        User,
        username=username,
    )
    
    users = user.profile.followers.all()
    tags = Tag.objects.all()
    
    user = request.user
    context = {
        "users": users,
        "user": user if user.is_authenticated else None,
        "tags": tags,
    }
    
    return render(request, 'blog/users.html', context)


@login_required
def user_edit(request, username):
    user = request.user
    profile, created = Profile.objects.get_or_create(user=user)

    
    form = ProfileForm(instance=profile,
                       initial = {
                           "first_name": user.first_name,
                           'last_name': user.last_name,
                           'bio': user.profile.bio,
                           'dp': user.profile.dp, 
                           "email": user.email
                       })
    

    # only the profile owner can edit
    if user.username.lower() != username.lower():
        messages.error(request, "Forbidden Action")
        return redirect('blog:profile', username=username)
    
    # handle form submition
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        
        if form.is_valid():
            form.save()
            
            if form.cleaned_data.get('password1'):
                update_session_auth_hash(request, request.user)

            return redirect('blog:user_edit', username = user.username)
        
        error_messages = form.errors.as_text()
        messages.error(request, error_messages)
        # return redirect('blog:user_edit', username = user.username)
        
    context = {
        "user": user,
        "form": form,
    }
    
    return render(request, 'blog/user_edit.html', context)


@login_required
def user_saved(request, username):
    user = request.user
    profile = get_object_or_404(
        User,
        username = username
    )

    if profile == user:
        posts = SavedPost.objects.filter(user=user).all()
        posts = [post.post for post in posts]
        page_title = "My Saved Posts 🔖"
    else:
        return redirect('blog:profile', username=username)
    
    
    context = {
        "user":user,
        "profile": profile,
        "posts": posts,
        "page_title": page_title,
    }
    return render(request, 'blog/home.html', context)


@login_required
def user_favorites(request, username):
    user = request.user
    profile = get_object_or_404(
        User,
        username = username
    )

    if profile == user:
        posts = PostReactions.objects.filter(user=user).all()
        posts = [post.post for post in posts]
        page_title = "My Favorites ❤"
    else:
        return redirect('blog:profile', username=username)
    
    
    context = {
        "user":user,
        "profile": profile,
        "posts": posts,
        "page_title": page_title,
    }
    return render(request, 'blog/home.html', context)


def profile(request, username):
    user = request.user
    profile = get_object_or_404(
        User,
        username = username
    )

    if profile == user:
        posts = Posts.objects.filter(author=profile)
        page_title = "My Posts"
    else:
        page_title = f"Explore {profile.username}'s Posts"
        posts = Posts.objects.filter(author=profile, status='PB')
    
    
    context = {
        "user":user if user.is_authenticated else None,
        "profile": profile,
        "posts": posts,
        "page_title": page_title,
    }
    return render(request, 'blog/profile.html', context)


@login_required
def user_follow(request, username):
    
    user = get_object_or_404(
        User,
        username = username,
        is_superuser = False
    )
    
    if user == request.user:
        return redirect('blog:profile', username=username)
        

    follower_profile, created = Profile.objects.get_or_create(user=request.user)
    followed_profile, created = Profile.objects.get_or_create(user=user)
    
    follower_profile.follow(followed_profile)
    return redirect('blog:profile', username=username)


@login_required
def user_unfollow(request, username):
    user = get_object_or_404(
        User,
        username = username,
        is_superuser = False
    )

        
    if user == request.user:
        return redirect('blog:profile', username=username)
        
        
    follower_profile, created = Profile.objects.get_or_create(user=request.user)
    followed_profile, created = Profile.objects.get_or_create(user=user)
    
    follower_profile.unfollow(followed_profile)
    
    
    return redirect('blog:profile', username=username)

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
            post.save(update=False)
            print(post.status)
            
            if tags:
                tags = tags.split(",")
                for tag in tags:
                    tag = tag.lower()
                    tag, created = Tag.objects.get_or_create(name=tag)
                    
                    post.tags.add(tag)
                    
            post.save(update=False)
            
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