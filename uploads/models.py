from django.db import models

# Create your models here.

class Upload(models.Model):
	author = models.IntegerField(default=0)
	name = models.CharField(max_length=50)
	uploaded_on = models.DateTimeField(auto_now=True)
	file = models.FileField(upload_to='uploads/', max_length=100)
	downloads = models.IntegerField()