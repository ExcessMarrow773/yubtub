from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.conf import settings
from yubtub import settings
from django.contrib.auth import get_user_model

import datetime
import cv2
import os
import re

User = get_user_model()

class Video(models.Model):
    author = models.CharField(max_length=100, default='admin')
    title = models.CharField(max_length=255)
    description = models.TextField(default='', null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to="thumbnail/", blank=True, height_field=None, width_field=None, max_length=None, null=True)
    views = models.IntegerField(default=0)
    viewedUsers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='watched_videos', blank=True)
    likes = models.IntegerField(default=0)
    likedUsers = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_videos', blank=True)
    video_file = models.FileField(
        upload_to='videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'wmv', 'flv', 'mkv', 'webm'])]
    )
    type = models.CharField(max_length=20, default='video')

    
    def was_published_recently(self):
            return self.created_on >= timezone.now() - datetime.timedelta(days=1)

    def generate_thumbnail(self):
        video_path = self.video_file.path
        thumbnail_path = video_path.rsplit('.', 1)[0] + '.jpg'
        filename = os.path.basename(thumbnail_path)
        thumbnail_path = os.path.join(settings.MEDIA_ROOT, 'thumbnail', filename)

        with open('debug.txt', 'w') as f:
            f.write("time: " + str(datetime.datetime.now()) + "\n")
            f.write(f"Video path: {video_path}\n")
            f.write(f"Thumbnail path: {thumbnail_path}\n")
            f.write(f"Video Exists: {os.path.exists(video_path)}\n")
            f.write(f"Thumbnail path includes 'thumbnail/': {'thumbnail/' in thumbnail_path}\n")

        cap = cv2.VideoCapture(video_path)
        success, image = cap.read()
        if success:
            cv2.imwrite(thumbnail_path, image)
            self.thumbnail = 'thumbnail/' + os.path.basename(thumbnail_path)
            with open('debug.txt', 'a') as f:
                f.write(f"Thumbnail generated at: {thumbnail_path}\n")
                f.write(f"Thumbnail Exists: {os.path.exists(thumbnail_path)}\n")
                f.write(f"Thumbnail success: {success}\n")
            print(f"Thumbnail generated at: {thumbnail_path}")

        cap.release()

        return os.path.join('thumbnail', filename)

    def save(self, *args, **kwargs):
        # Ensure empty descriptions become the default before saving
        if not self.description or self.description.isspace():
            self.description = "There was no description provided for this video"

        # Track kwargs so we can avoid re-using force_insert/force_update on subsequent saves
        first_save_kwargs = kwargs.copy()

        # First save to create the row and get a primary key (if new)
        super().save(*args, **kwargs)

        # If no thumbnail yet, try to generate one and update just the thumbnail field.
        # Remove any force_insert/force_update flags before doing the update save.
        if not self.thumbnail and getattr(self, 'video_file', None):
            try:
                self.generate_thumbnail()
                # avoid re-using force_insert/force_update on update
                update_kwargs = {}
                update_kwargs.update(first_save_kwargs)
                update_kwargs.pop('force_insert', None)
                update_kwargs.pop('force_update', None)
                super().save(update_fields=['thumbnail'], **update_kwargs)
            except Exception:
                # thumbnail generation should not break saving the model during tests
                pass

    def __str__(self):
        return self.title

class VideoComment(models.Model):
    author = models.CharField(max_length=60)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    video = models.ForeignKey("Video", on_delete=models.CASCADE)
    type = models.CharField(max_length=20, default='videoComment')

    def __str__(self):
         return self.author
    
    def get_mentions(self):
        """Extract all @mentions from the comment body"""
        pattern = r'@(\w+)'
        mentions = re.findall(pattern, self.body)
        return mentions
    
    def get_valid_mentions(self):
        """Return only usernames that exist in the database"""
        mentioned_usernames = self.get_mentions()
        valid_users = User.objects.filter(username__in=mentioned_usernames)
        return list(valid_users.values_list('username', flat=True))

class Post(models.Model):
    author = models.CharField(max_length=100, default='admin')
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    type = models.CharField(max_length=20, default='post')

    def was_published_recently(self):
       return self.created_on >= timezone.now() - datetime.timedelta(days=1)
    
    def __str__(self):
        return self.title

class PostComment(models.Model):
    author = models.CharField(max_length=60)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey("Post", on_delete=models.CASCADE)
    type = models.CharField(max_length=20, default='postComment')

    def __str__(self):
         return self.author
    
    def get_mentions(self):
        """Extract all @mentions from the comment body"""
        pattern = r'@(\w+)'
        mentions = re.findall(pattern, self.body)
        return mentions
    
    def get_valid_mentions(self):
        """Return only usernames that exist in the database"""
        mentioned_usernames = self.get_mentions()
        valid_users = User.objects.filter(username__in=mentioned_usernames)
        return list(valid_users.values_list('username', flat=True))

