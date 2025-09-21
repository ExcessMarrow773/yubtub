from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.files.base import ContentFile
import datetime
import ffmpeg
from PIL import Image
import io


class Video(models.Model):
    def generate_thumbnail(self):

        # Path to the uploaded video file
        video_path = self.video_file.path

        # Generate thumbnail using ffmpeg
        thumbnail_path = f"{video_path[:len(video_path)-4]}.jpg"

        with open("debug.txt", 'w') as f:
            f.write(f"Video path: {video_path}\n")
            f.write(f"Thumbnail path: {thumbnail_path}\n")
        try:
            (
                ffmpeg
                .input(video_path, ss=1)  # Capture frame at 1 second
                .output(thumbnail_path, vframes=1)
                .run(capture_stdout=True, capture_stderr=True)
            )
            # Save the thumbnail to the ImageField
            with open(thumbnail_path, 'rb') as f:
                image = Image.open(f)
                thumb_io = io.BytesIO()
                image.save(thumb_io, format='JPEG')
                self.thumbnail.save(f"{self.pk}_thumbnail.jpg", ContentFile(thumb_io.getvalue()), save=False)
        except Exception as e:
            print(f"Error generating thumbnail: {e}")
            with open("debug.txt", 'a') as f:
                f.write(f"Error generating thumbnail: {e}\n")


    author = models.CharField(max_length=100, default='admin')
    title = models.CharField(max_length=255)
    description = models.TextField(default='', null=True, blank=True)
    posted_on = models.DateTimeField(auto_now_add=True)
    thumbnail = models.ImageField(upload_to="thumbnail", blank=True, height_field=None, width_field=None, max_length=None, null=True)
    views = models.IntegerField(default=0)
    video_file = models.FileField(
        upload_to='videos/',
        validators=[FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'wmv', 'flv', 'mkv', 'webm'])]
    )
    def was_published_recently(self):
            return self.created_on >= timezone.now() - datetime.timedelta(days=1)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        print(self.thumbnail)
        if self.thumbnail == None or self.thumbnail == "":
            self.generate_thumbnail()
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