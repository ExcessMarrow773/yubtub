from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core import validators
from django.utils.translation import gettext_lazy as _

# Create your models here.

class CustomUsernameValidator(UnicodeUsernameValidator):
    regex = r'^[\w+-]+$'  # Modify this regex to allow/disallow characters
    message = _(
        'Enter a valid username. This value may contain only letters, '
        'numbers, and ./-/_ characters.'
    )

class CustomUser(AbstractUser):
	username_validator = CustomUsernameValidator()

	following = models.ManyToManyField('self', symmetrical=False, related_name='followers', blank=True)

	username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
		help_text=_(
            'Required. 150 characters or fewer. Letters, digits and +/-/_ only.'
        ),
    )

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