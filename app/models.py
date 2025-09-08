from django.db import models
from django.utils import timezone
import datetime

class Video(models.Model):
    author = models.CharField(max_length=100, default='admin')
    title = models.CharField(max_length=255)
    description = models.TextField()
    posted_on = models.DateTimeField(auto_now_add=True)
    video_file = models.FileField(upload_to='videos/')    
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