from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils import timezone
from app.models import Video, Comment, Post

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']

class PostVideo(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'thumbnail', 'video_file']

class CreatePost(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body']
    