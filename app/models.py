from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
import datetime

class Video(models.Model):
    author = models.CharField(max_length=100, default='admin')
    title = models.CharField(max_length=255)
    description = models.TextField(default='There was no description provided for this video')
    posted_on = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to="thumbnail", height_field=None, width_field=None, max_length=None)
    views = models.IntegerField(default=0)
    video_file = models.FileField(
        upload_to='videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'wmv', 'flv', 'mkv', 'webm'])]
    )    
    def was_published_recently(self):
            return self.created_on >= timezone.now() - datetime.timedelta(days=1)
    def __str__(self):
        return self.title

class Comment(models.Model):
    author = models.CharField(max_length=60)
    body = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    video = models.ForeignKey("Video", on_delete=models.CASCADE)
    def __str__(self):
         return self.author