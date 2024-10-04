from django.contrib import admin
from .models import Posts
import random

# Register your models here.
@admin.register(Posts)
class PostsModel(admin.ModelAdmin):
    list_display = ['title', 'link', 'author', 'publish', 'status']
    list_filter = ['status', 'created', 'publish', 'author']
    search_fields = ['title', 'body']
    prepopulated_fields = {'link': ('title', )}
    raw_id_fields = ['author']
    date_hierarchy = 'publish'
    ordering = ['status', 'publish']
    show_facets = admin.ShowFacets.ALWAYS