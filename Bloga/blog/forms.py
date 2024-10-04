from django import forms

from .models import Posts

class PostsForm(forms.ModelForm):
    title = forms.CharField(
        required=True,
        widget=forms.TextInput(
            attrs={
                "class": "w-full text-6xl blog",
                "placeholder": "Blog Title",
            }
        )
    )
    
    tags = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={"id": "tags", "class": "hidden"}
        )
    )
    
    content = forms.CharField(
        widget=forms.Textarea(
            attrs={
                "id": "content",
                "name": "content",
                "class": "blog",
                "placeholder": "Start writing here"
            }
        ),
        required=True,
    )
    
    status = forms.ChoiceField(
        choices=Posts.Status,
        widget=forms.Select(
            attrs={"class": "hidden", "id": "status"}
        )
    )
    
    class Meta:
        model = Posts
        fields = ['title', 'tags', 'content', 'status']