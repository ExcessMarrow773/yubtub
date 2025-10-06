from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils import timezone
from app.models import Video, VideoComment, Post, PostComment

class VideoCommentForm(forms.ModelForm):
    class Meta:
        model = VideoComment
        fields = ['body']

class PostVideo(forms.ModelForm):
    class Meta:
        model = Video
        fields = ['title', 'description', 'thumbnail', 'video_file']

class CreatePost(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'body']

class PostCommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ['body']