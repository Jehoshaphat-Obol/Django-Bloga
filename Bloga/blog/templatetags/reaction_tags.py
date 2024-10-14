from django import template

from ..models import CommentReactions, PostReactions, SavedPost

register = template.Library()

@register.simple_tag
def likes_post(post, user):
    return PostReactions.objects.filter(post=post, user=user).exists()

@register.simple_tag
def likes_comment(comment, user):
    return CommentReactions.objects.filter(comment=comment, user=user).exists()

@register.simple_tag
def post_saved(post, user):
    return SavedPost.objects.filter(user=user, post=post).exists()