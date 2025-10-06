from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from yubtub import settings
import datetime
import cv2
import os
from django.contrib.auth.models import User

class Video(models.Model):
    author = models.CharField(max_length=100, default='admin')
    title = models.CharField(max_length=255)
    description = models.TextField(default='', null=True, blank=True)
    posted_on = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to="thumbnail", blank=True, height_field=None, width_field=None, max_length=None, null=True)
    views = models.IntegerField(default=0)
    viewedUsers = models.ManyToManyField(User, related_name='watched_videos', blank=True)
    likes = models.IntegerField(default=0)
    likedUsers = models.ManyToManyField(User, related_name='liked_videos', blank=True)
    video_file = models.FileField(
        upload_to='videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'wmv', 'flv', 'mkv', 'webm'])]
    )
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
            self.thumbnail = 'videos/' + os.path.basename(thumbnail_path)
            with open('debug.txt', 'a') as f:
                f.write(f"Thumbnail generated at: {thumbnail_path}\n")
                f.write(f"Thumbnail Exists: {os.path.exists(thumbnail_path)}\n")
                f.write(f"Thumbnail success: {success}\n")
            print(f"Thumbnail generated at: {thumbnail_path}")

        cap.release()

        return os.path.join('thumbnail', filename)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print(self.thumbnail)
        if self.thumbnail == None or self.thumbnail == "":
            self.thumbnail = self.generate_thumbnail()
            super().save(*args, **kwargs)  # Save again to store the thumbnail

        if self.description == "":
            self.description = "There was no description provided for this video"
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.CharField(max_length=60)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    video = models.ForeignKey("Video", on_delete=models.CASCADE)
    def __str__(self):
         return self.author

class Post(models.Model):
    author = models.CharField(max_length=100, default='admin')
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def was_published_recently(self):
            return self.created_on >= timezone.now() - datetime.timedelta(days=1)
    def __str__(self):
        return self.title