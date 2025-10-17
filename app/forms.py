from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils import timezone
from app.models import Video, VideoComment, Post, PostComment
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "password1", "password2")

class CustomAuthenticationForm(AuthenticationForm):
    pass

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
        fields = ['title', 'body', 'image']

class PostCommentForm(forms.ModelForm):
    class Meta:
        model = PostComment
        fields = ['body']