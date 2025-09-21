from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.utils import timezone

class CommentForm(forms.Form):
    body = forms.CharField(
        max_length=255,
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Leave a comment!"}
        )
    )

class PostVideo(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Title"}
        ),
    )
    thumbnail = forms.ImageField(
        widget=forms.FileInput(
            attrs={"class": "form-control", "required": "False"}
        )
    )
    description = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Body"}
        )
    )
    video = forms.FileField(required=True)