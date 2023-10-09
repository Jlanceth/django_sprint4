from django import forms
from django.contrib.auth import get_user_model

from .models import Post, Comment


User = get_user_model()


class ProfileUpdateForm(forms.ModelForm):

    class Meta:
        model = User

        fields = ['first_name', 'last_name', 'username', 'email']


class PostForm(forms.ModelForm):

    class Meta:
        model = Post

        fields = ['title', 'text', 'pub_date', 'location', 'image', 'category']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
