from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.

class CustomUser(AbstractUser):
	following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

	def follow(self, user):
		self.following.add(user)

	def unfollow(self, user):
		self.following.remove(user)

	def follower_count(self):
		return len(self.followers.all())

	def is_following(self, user):
		return self.following.filter(pk=user.pk).exists()

	def is_followed_by(self, user):
		return self.followers.filter(pk=user.pk).exists()