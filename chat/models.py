from django.db import models
from django.conf import settings
from datetime import datetime
from django.utils import timezone
# Avoid importing the user model at import-time to keep migrations portable.
def _get_sentinel_user_pk():
	"""Return a pk for a sentinel/system user, creating it if needed.

	This callable is safe to use as a field default because Django will
	serialize the dotted path. It will create a lightweight "system" user
	when first needed (for example during migrations) so foreign keys can
	have a sensible default while remaining non-nullable.
	"""
	from django.contrib.auth import get_user_model

	UserModel = get_user_model()
	user, _created = UserModel.objects.get_or_create(
		username="system",
		defaults={
			"email": "system@example.local",
			# mark inactive so it isn't used for login
			"is_active": False,
		},
	)
	return user.pk


# Create your models here.
User = settings.AUTH_USER_MODEL


class Message(models.Model):
	# keep the fields required (non-nullable) but provide a callable default
	# which ensures a sentinel user exists and returns its primary key.
	from_user = models.ForeignKey(
		User,
		related_name="from_user",
		on_delete=models.CASCADE,
		default=_get_sentinel_user_pk,
	)
	to_user = models.ForeignKey(
		User,
		related_name="to_user",
		on_delete=models.CASCADE,
		default=_get_sentinel_user_pk,
	)
	body = models.TextField()
	sent_on = models.DateTimeField(auto_now_add=True, blank=False)


	class Meta:
		verbose_name = "Message"
		verbose_name_plural = "Messages"
		ordering = ("sent_on",)

	def __str__(self):
		# avoid referencing a non-existent `chat` attribute
		return f"Message {self.id} from {self.from_user} to {self.to_user}"
